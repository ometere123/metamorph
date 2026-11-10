// Read-only StudioNet evidence verifier.  No wallet, private key or write
// method is used.  Missing historical transaction indexing is reported as a
// limitation, while contradicted state or source claims exit nonzero.
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const RPC = "https://studio.genlayer.com/api";
const EXPECTED_CHAIN = "0xf22f";
const EXPLORER = "https://explorer-studio.genlayer.com";
const configArg = process.argv.find((arg) => arg.startsWith("--config="));
const fullOutput = process.argv.includes("--full");
const configPath = configArg ? path.resolve(ROOT, configArg.slice("--config=".length))
  : path.join(ROOT, "scripts", "live_evidence_config.json");

const failures = [];
const warnings = [];
const output = {rpc: RPC, explorer: EXPLORER, checks: {}, transactions: [], sources: [], reads: []};

async function rpc(method, params = []) {
  const response = await fetch(RPC, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({jsonrpc: "2.0", id: Date.now(), method, params}),
  });
  if (!response.ok) throw new Error(`RPC HTTP ${response.status}`);
  const body = await response.json();
  if (body.error) throw new Error(`${method}: ${JSON.stringify(body.error)}`);
  return body.result;
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function normalizeSource(value) {
  return value.replace(/\r\n/g, "\n");
}

async function readContract(client, address, functionName, args = []) {
  return client.readContract({address, functionName, args});
}

async function checkChain() {
  const chainId = await rpc("eth_chainId");
  output.checks.chain_id = {actual: chainId, expected: EXPECTED_CHAIN, ok: chainId?.toLowerCase() === EXPECTED_CHAIN};
  if (!output.checks.chain_id.ok) failures.push(`live eth_chainId=${chainId}, expected ${EXPECTED_CHAIN}`);
}

async function checkState(client, config) {
  const counts = await readContract(client, config.registry, "get_counts");
  output.reads.push({address: config.registry, method: "get_counts", value: counts});
  for (const run of config.runs || []) {
    try {
      const raw = await readContract(client, config.registry, "get_run", [run.id]);
      const state = raw ? JSON.parse(raw) : null;
      const historical = await readContract(client, config.registry, "is_certified", [
        run.id, run.suite, run.target, run.digest,
      ]);
      const current = await readContract(client, config.registry, "is_certified_current", [
        run.id, run.suite, run.target, run.digest,
      ]);
      const ok = Boolean(state && state.outcome === run.outcome &&
        Boolean(historical) === Boolean(run.certified) && Boolean(current) === Boolean(run.certified));
      output.reads.push({label: run.label, run: state, historical, current, ok});
      if (!ok) failures.push(`run claim contradicted: ${run.label}`);
    } catch (error) {
      failures.push(`unable to verify run ${run.label}: ${error.message}`);
    }
  }
  for (const consumer of config.consumers || []) {
    try {
      const raw = await readContract(client, consumer.address, "status");
      const state = typeof raw === "string" ? JSON.parse(raw) : raw;
      const ok = Boolean(state?.activated) === Boolean(consumer.expected_activated) &&
        state?.run_id === consumer.expected_run;
      output.reads.push({label: consumer.label, address: consumer.address, status: state, ok});
      if (!ok) failures.push(`consumer claim contradicted: ${consumer.label}`);
    } catch (error) {
      failures.push(`unable to verify consumer ${consumer.label}: ${error.message}`);
    }
  }
}

function transactionSummary(tx) {
  if (!tx) return null;
  const leader = tx.consensus_data?.leader_receipt?.[0];
  return {
    hash: tx.hash,
    from_address: tx.from_address,
    to_address: tx.to_address,
    status: tx.statusName ?? tx.status,
    result: tx.resultName ?? tx.result,
    tx_id: tx.tx_id,
    created_timestamp: tx.created_timestamp,
    contract_address: tx.data?.contract_address,
    tx_execution_hash: tx.data?.tx_execution_hash,
    leader_execution: leader?.execution_result,
    validator_executions: (tx.consensus_data?.validators || []).map((item) => item.execution_result),
  };
}

function receiptSummary(receipt) {
  if (!receipt) return null;
  return {
    transactionHash: receipt.transactionHash,
    blockHash: receipt.blockHash,
    blockNumber: receipt.blockNumber,
    status: receipt.status,
    logs: Array.isArray(receipt.logs) ? receipt.logs.length : undefined,
  };
}

async function checkSources(client) {
  const manifest = JSON.parse(await fs.readFile(path.join(ROOT, "SOURCE_SHA256_MANIFEST.json"), "utf8"));
  for (const [relative, entry] of Object.entries(manifest.files)) {
    const localRaw = await fs.readFile(path.join(ROOT, relative), "utf8");
    const localCanonical = sha256(Buffer.from(normalizeSource(localRaw), "utf8"));
    const localOk = localCanonical.toLowerCase() === entry.sha256.toLowerCase();
    if (!localOk) failures.push(`local source hash mismatch: ${relative}`);
    for (const address of entry.deployed_addresses || []) {
      try {
        const deployed = await client.getContractCode(address);
        const deployedHash = sha256(Buffer.from(deployed, "utf8"));
        const deployedOk = deployedHash.toLowerCase() === String(entry.deployed_sha256 || "").toLowerCase();
        output.sources.push({file: relative, address, local_canonical: localCanonical,
          deployed_raw: deployedHash, local_ok: localOk, deployed_ok: deployedOk});
        if (!deployedOk) failures.push(`deployed source hash mismatch: ${relative} at ${address}`);
      } catch (error) {
        failures.push(`unable to fetch deployed source ${relative} at ${address}: ${error.message}`);
      }
    }
  }
}

async function checkTransactions(config) {
  for (const hash of config.transactions || []) {
    const item = {hash, explorer: `${EXPLORER}/tx/${hash}`};
    try {
      const transaction = await rpc("eth_getTransactionByHash", [hash]);
      item.eth_transaction = fullOutput ? transaction : transactionSummary(transaction);
    }
    catch (error) { item.eth_transaction_error = error.message; }
    try {
      const receipt = await rpc("eth_getTransactionReceipt", [hash]);
      item.eth_receipt = fullOutput ? receipt : receiptSummary(receipt);
    }
    catch (error) { item.eth_receipt_error = error.message; }
    item.indexed = Boolean(item.eth_transaction || item.eth_receipt);
    if (!item.indexed) warnings.push(`historical transaction not returned by required eth RPC: ${hash}`);
    output.transactions.push(item);
  }
}

try {
  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  await checkChain();
  const client = createClient({chain: studionet, endpoint: RPC});
  await checkState(client, config);
  await checkSources(client);
  await checkTransactions(config);
} catch (error) {
  failures.push(error.message);
}

output.ok = failures.length === 0;
output.full_receipts = fullOutput;
output.failures = failures;
output.warnings = warnings;
console.log(JSON.stringify(output, null, 2));
if (failures.length > 0) process.exitCode = 1;
