const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    // Show exact first 20 chars as hex
    const first50 = code.slice(0, 50);
    console.log("First 50 chars:", JSON.stringify(first50));
    console.log("Char codes:");
    for (let i = 0; i < Math.min(20, code.length); i++) {
      console.log(`  [${i}] U+${code.charCodeAt(i).toString(16).padStart(4,'0')} ${JSON.stringify(code[i])}`);
    }
    
    // Check if there's a BOM or special character
    if (code.charCodeAt(0) === 0xFEFF) {
      console.log("WARNING: BOM detected at start of block 6!");
    }
    
    // Try parsing just the first few lines
    const lines = code.split('\n');
    for (let i = 1; i <= 5; i++) {
      const partial = 'async function __test__() {\n' + lines.slice(0, i).join('\n') + '\n}';
      try {
        new Function(partial);
        console.log(`Lines 1-${i}: OK`);
      } catch(e) {
        console.log(`Lines 1-${i}: ERROR - ${e.message}`);
        console.log(`Line ${i}: ${JSON.stringify(lines[i-1])}`);
      }
    }
  }
}
