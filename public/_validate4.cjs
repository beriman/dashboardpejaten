const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  const code = match[1];
  
  // Wrap in async function to make it valid for parsing
  const wrapped = 'async function __test__() {\n' + code + '\n}';
  try {
    new Function(wrapped);
    console.log(`Block ${blockNum}: OK (${code.length} chars)`);
  } catch (e) {
    console.log(`Block ${blockNum}: ERROR - ${e.message}`);
    // Try to find the line
    const beforeBlock = content.substring(0, match.index);
    const lineNumber = beforeBlock.split('\n').length;
    console.log(`  Block starts at approx line ${lineNumber}`);
    
    // Binary search for error
    const lines = code.split('\n');
    let lo = 0, hi = lines.length;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      const partial = 'async function __test__() {\n' + lines.slice(0, mid).join('\n') + '\n}';
      try {
        new Function(partial);
        lo = mid + 1;
      } catch(e) {
        hi = mid;
      }
    }
    console.log(`  Error near line ${lo} of block (abs line ~${lineNumber + lo})`);
    console.log(`  Context:`);
    for (let i = Math.max(0, lo-3); i < Math.min(lines.length, lo+2); i++) {
      console.log(`    L${i+1}: ${lines[i]}`);
    }
  }
}
