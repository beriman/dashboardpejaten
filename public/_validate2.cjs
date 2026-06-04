const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    // Show last 200 chars
    console.log("Last 500 chars of block 6:");
    console.log(code.slice(-500));
    console.log("\n---");
    // Show first 100 chars
    console.log("First 100 chars of block 6:");
    console.log(code.slice(0, 100));
    
    // Try parsing smaller chunks to find the error
    console.log("\n--- Trying to find error location ---");
    // Split in half and try each half
    const mid = Math.floor(code.length / 2);
    try { new Function(code.slice(0, mid)); console.log("First half: OK"); } catch(e) { console.log("First half: ERROR"); }
    try { new Function(code.slice(mid)); console.log("Second half: OK"); } catch(e) { console.log("Second half: ERROR"); }
  }
}
