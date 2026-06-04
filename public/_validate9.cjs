const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1].replace(/\r/g, '');
    const lines = code.split('\n');
    
    // Try parsing first 10 lines
    const first10 = lines.slice(0, 10).join('\n');
    console.log("First 10 lines:");
    console.log(first10);
    console.log("\n---");
    
    try {
      new Function('async function __test__() {\n' + first10 + '\n}');
      console.log("First 10 lines: OK");
    } catch(e) {
      console.log("First 10 lines: ERROR -", e.message);
      
      // Try each line individually
      for (let i = 0; i < 10; i++) {
        try {
          new Function('async function __test__() {\n' + lines.slice(0, i+1).join('\n') + '\n}');
        } catch(e) {
          console.log(`Error at line ${i+1}: ${e.message}`);
          console.log(`Content: ${JSON.stringify(lines[i])}`);
          break;
        }
      }
    }
    break;
  }
}
