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
    
    // Line 209 of block 6
    console.log("=== Line 209 of block 6 ===");
    for (let i = 205; i < Math.min(lines.length, 215); i++) {
      const marker = (i === 208) ? '>>>' : '   ';
      console.log(`${marker} L${i+1}: ${lines[i]}`);
    }
    
    // Also check: what's the context around line 209?
    // Look for the function/block that contains line 209
    console.log("\n=== Wider context (L195-L225) ===");
    for (let i = 194; i < Math.min(lines.length, 225); i++) {
      const marker = (i === 208) ? '>>>' : '   ';
      console.log(`${marker} L${i+1}: ${lines[i]}`);
    }
    
    break;
  }
}
