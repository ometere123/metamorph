// Small, secret-free StudioNet integration harness.
//
// It reads encrypted CLI keystores only in memory, prompts for their password,
// and emits one concise JSON receipt per command. It is intentionally not an
// application backend and is not used by the contracts themselves.
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { Wallet } from "ethers";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { CalldataAddress, TransactionStatus } from "genlayer-js/types";

const RPC = "https://studio.genlayer.com/api";
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
  const rl = readline.createInterface({ input, output });
  password = await rl.question("Keystore password: ");
  rl.close();
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
    leader_execution: leader?.execution_result,
    validator_executions: (receipt.consensus_data?.validators || []).map((item) => item.execution_result),
    contract_address: receipt.data?.contract_address,
    return_data: receipt.data?.return_data,
    created_at: receipt.created_at,
  };
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
    if (command.op === "write") return await write(command);
    if (command.op === "read") return await read(command);
    throw new Error("op must be write or read");
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
}

const rl = readline.createInterface({ input, output, terminal: Boolean(output.isTTY) });
// Prompt once on the same readline interface used for commands. A nested
// readline instance corrupts stdin on Windows PTYs and can turn password
// characters into phantom commands.
await rl.question("Keystore password: ").then((value) => { password = value; });
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
