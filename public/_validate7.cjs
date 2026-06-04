const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    // Split by \n and check each line's \r status
    const lines = code.split('\n');
    console.log(`Total lines: ${lines.length}`);
    console.log(`Line 1 length: ${lines[0].length}, ends with \\r: ${lines[0].endsWith('\r')}`);
    console.log(`Line 2 length: ${lines[1].length}, ends with \\r: ${lines[1].endsWith('\r')}`);
    console.log(`Line 1: ${JSON.stringify(lines[0])}`);
    console.log(`Line 2: ${JSON.stringify(lines[1])}`);
    
    // Try: join with \n only (no \r)
    const codeNoCR = code.replace(/\r/g, '');
    const wrapped = 'async function __test__() {\n' + codeNoCR + '\n}';
    try {
      new Function(wrapped);
      console.log("\nWithout CR: PARSES OK");
    } catch(e) {
      console.log("\nWithout CR: ERROR -", e.message);
    }
    
    // Try with original
    const wrapped2 = 'async function __test__() {\n' + code + '\n}';
    try {
      new Function(wrapped2);
      console.log("With original: PARSES OK");
    } catch(e) {
      console.log("With original: ERROR -", e.message);
    }
    break;
  }
}
