const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

// Extract block 6
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    console.log("Block 6 length:", code.length);
    console.log("Last 200 chars:");
    console.log(JSON.stringify(code.slice(-200)));
    console.log("\nFirst 100 chars:");
    console.log(JSON.stringify(code.slice(0, 100)));
    
    // Check: does the block itself parse?
    // Use vm.runInNewContext to avoid Function() scope issues
    const vm = require('vm');
    try {
      vm.runInNewContext(code, {}, { timeout: 5000 });
      console.log("\nBlock 6: PARSES OK");
    } catch (e) {
      console.log("\nBlock 6 PARSE ERROR:", e.message);
    }
  }
}
