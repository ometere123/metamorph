// Independent live-RPC assertion. This does not trust the CLI network alias.
const RPC = 'https://studio.genlayer.com/api';
const EXPECTED_HEX = '0xf22f';
const EXPECTED_DECIMAL = 61999;

const response = await fetch(RPC, {
  method: 'POST',
  headers: {'content-type': 'application/json'},
  body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'eth_chainId', params: []}),
});
if (!response.ok) throw new Error(`StudioNet RPC HTTP ${response.status}`);
const body = await response.json();
if (body.error) throw new Error(`StudioNet RPC error: ${JSON.stringify(body.error)}`);
if (typeof body.result !== 'string' || body.result.toLowerCase() !== EXPECTED_HEX) {
  throw new Error(`Unexpected live chain ID: ${body.result}; expected ${EXPECTED_HEX}`);
}
const decimal = Number.parseInt(body.result, 16);
if (decimal !== EXPECTED_DECIMAL) throw new Error(`Unexpected decimal chain ID: ${decimal}`);
console.log(`PASS: live ${RPC} eth_chainId=${body.result} (${decimal})`);
