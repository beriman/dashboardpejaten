const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    const lines = code.split('\n');
    
    // Find dataSets declaration
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes('dataSets')) {
        console.log(`L${i+1}: ${lines[i].trim()}`);
      }
    }
    
    // Find all top-level structure around dataSets
    // Look for the pattern: const dataSets = { ... };
    console.log("\n=== dataSets structure ===");
    let inDataSets = false;
    let depth = 0;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith('const dataSets')) {
        inDataSets = true;
        console.log(`L${i+1} (depth=${depth}): ${line}`);
        depth += (line.match(/{/g) || []).length - (line.match(/}/g) || []).length;
        continue;
      }
      if (inDataSets) {
        const o = (line.match(/{/g) || []).length;
        const c = (line.match(/}/g) || []).length;
        depth += o - c;
        if (depth <= 0) {
          console.log(`L${i+1} (depth=${depth}): ${line}  <-- CLOSES dataSets`);
          inDataSets = false;
        }
      }
    }
    
    break;
  }
}
