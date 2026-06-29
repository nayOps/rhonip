import fs from 'fs';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const file = process.argv[2] || 'src/components/forms/BaseEnrollmentForm.tsx';
const code = fs.readFileSync(file, 'utf8');

// Next bundles @swc/wasm
const swcPath = require.resolve('next/dist/build/swc');
const swc = require(swcPath);

async function main() {
  try {
    const result = await swc.transform(code, {
      filename: file,
      jsc: { parser: { syntax: 'typescript', tsx: true } },
    });
    console.log('OK', result.code?.length ?? 0, 'bytes');
  } catch (e) {
    console.error('FAIL', e.message || e);
    process.exit(1);
  }
}

main();
