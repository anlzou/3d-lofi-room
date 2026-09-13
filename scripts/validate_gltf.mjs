import fs from 'node:fs';
import { validateBytes } from 'gltf-validator';
const bytes = fs.readFileSync(new URL('../public/models/demo.glb', import.meta.url));
// Lightmap UVs are consumed by the Three.js runtime, not by a glTF material slot.
const report = await validateBytes(new Uint8Array(bytes), { uri: 'demo.glb', maxIssues: 100000, ignoredIssues: ['UNUSED_OBJECT'] });
fs.writeFileSync(new URL('../docs/gltf-validation.json', import.meta.url), JSON.stringify(report, null, 2));
const counts = {};
for (const message of report.issues.messages) counts[message.code] = (counts[message.code] ?? 0) + 1;
console.log(JSON.stringify({ errors: report.issues.numErrors, warnings: report.issues.numWarnings, codes: counts }, null, 2));
if (report.issues.numErrors) process.exitCode = 1;
