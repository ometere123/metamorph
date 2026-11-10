// Small, secret-free StudioNet integration harness.
//
// It reads encrypted CLI keystores only in memory, prompts for their password,
// and emits one concise JSON receipt per command. It is intentionally not an
// application backend and is not used by the contracts themselves.
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";
import { stdin as input, stdout as output } from "node:process";
import { Wallet } from "ethers";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { CalldataAddress, TransactionStatus } from "genlayer-js/types";

const RPC = "https://studio.genlayer.com/api";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const home = os.homedir();
const genlayerHome = process.env.GENLAYER_HOME || path.join(home, ".genlayer");
const keystoreDir = path.join(genlayerHome, "keystores");

let password;
const accounts = new Map();
const clients = new Map();

function typedAddress(hex) {
  if (typeof hex !== "string" || !/^0x[0-9a-fA-F]{40}$/.test(hex)) {
    throw new Error("address marker must contain a 20-byte 0x address");
  }
  return new CalldataAddress(Uint8Array.from(Buffer.from(hex.slice(2), "hex")));
}

function decodeValue(value) {
  if (Array.isArray(value)) return value.map(decodeValue);
  if (value && typeof value === "object") {
    if (Object.keys(value).length === 1 && typeof value.__address === "string") {
      return typedAddress(value.__address);
    }
    if (Object.keys(value).length === 1 && typeof value.__bytes === "string") {
      if (!/^0x[0-9a-fA-F]*$/.test(value.__bytes)) throw new Error("invalid bytes marker");
      return Uint8Array.from(Buffer.from(value.__bytes.slice(2), "hex"));
    }
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, decodeValue(item)]));
  }
  return value;
}

async function getPassword() {
  if (password !== undefined) return password;
  if (!input.isTTY || !output.isTTY || typeof input.setRawMode !== "function") {
    throw new Error("Secure keystore password entry requires an interactive TTY; no password was read");
  }
  password = await new Promise((resolve, reject) => {
    let value = "";
    let finished = false;
    const cleanup = () => {
      if (finished) return;
      finished = true;
      input.off("data", onData);
      input.setRawMode(false);
      input.pause();
    };
    const fail = (error) => {
      cleanup();
      output.write("\n");
      reject(error);
    };
    const onData = (chunk) => {
      for (const char of chunk.toString("utf8")) {
        if (char === "\u0003") {
          fail(new Error("Password entry cancelled"));
          return;
        }
        if (char === "\r" || char === "\n") {
          cleanup();
          output.write("\n");
          resolve(value);
          return;
        }
        if (char === "\b" || char === "\u007f") {
          if (value.length > 0) {
            value = value.slice(0, -1);
            output.write("\b \b");
          }
          continue;
        }
        if (char >= " ") {
          value += char;
          output.write("*");
        }
      }
    };
    input.setRawMode(true);
    input.resume();
    input.on("data", onData);
    output.write("Keystore password: ");
  });
  return password;
}

async function getAccount(name) {
  if (!accounts.has(name)) {
    const file = path.join(keystoreDir, `${name}.json`);
    const encrypted = await fs.readFile(file, "utf8");
    const wallet = await Wallet.fromEncryptedJson(encrypted, await getPassword());
    accounts.set(name, createAccount(wallet.privateKey));
  }
  return accounts.get(name);
}

async function getClient(name) {
  if (!clients.has(name)) {
    clients.set(name, createClient({ chain: studionet, endpoint: RPC, account: await getAccount(name) }));
  }
  return clients.get(name);
}

function summary(receipt, hash) {
  const leader = receipt.consensus_data?.leader_receipt?.[0];
  return {
    ok: true,
    hash,
    status: receipt.status_name ?? receipt.status,
    result: receipt.result_name ?? receipt.result,
    execution_result: receipt.tx_execution_result_name ?? receipt.txExecutionResultName ??
      receipt.execution_result_name ?? receipt.executionResultName ?? receipt.result_name ?? receipt.result,
    leader_execution: leader?.execution_result,
    validator_executions: (receipt.consensus_data?.validators || []).map((item) => item.execution_result),
    contract_address: receipt.data?.contract_address,
    return_data: receipt.data?.return_data,
    created_at: receipt.created_at,
  };
}

async function deploy(command) {
  const client = await getClient(command.account);
  const contractPath = path.resolve(ROOT, command.contract);
  const relative = path.relative(ROOT, contractPath);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error("contract path must remain inside the repository");
  }
  const code = await fs.readFile(contractPath, "utf8");
  const hash = await client.deployContract({
    code,
    args: (command.args || []).map(decodeValue),
    leaderOnly: false,
  });
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.FINALIZED,
    interval: 5000,
    retries: 120,
  });
  return summary(receipt, hash);
}

async function write(command) {
  const client = await getClient(command.account);
  const args = (command.args || []).map(decodeValue);
  const hash = await client.writeContract({
    address: command.contract,
    functionName: command.method,
    args,
    value: BigInt(0),
    leaderOnly: false,
  });
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.FINALIZED,
    interval: 5000,
    retries: 120,
  });
  return summary(receipt, hash);
}

async function read(command) {
  const client = createClient({ chain: studionet, endpoint: RPC });
  const value = await client.readContract({
    address: command.contract,
    functionName: command.method,
    args: (command.args || []).map(decodeValue),
  });
  return { ok: true, value };
}

async function handle(command) {
  try {
    if (command.op === "deploy") return await deploy(command);
    if (command.op === "write") return await write(command);
    if (command.op === "read") return await read(command);
    throw new Error("op must be deploy, write or read");
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
}

// Password input is deliberately collected before readline is created.  Raw
// TTY mode masks each character on Windows and Unix; non-interactive stdin is
// rejected instead of accepting a password that could be echoed or logged.
await getPassword();
const rl = readline.createInterface({ input, output, terminal: Boolean(output.isTTY) });
for await (const line of rl) {
  if (!line.trim()) continue;
  if (line.trim() === "exit") break;
  let command;
  try {
    command = JSON.parse(line);
  } catch (error) {
    console.log(JSON.stringify({ ok: false, error: "invalid command JSON" }));
    continue;
  }
  console.log(JSON.stringify(await handle(command)));
}
rl.close();
