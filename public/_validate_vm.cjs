const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    // Remove \r and write to temp
    const code = match[1].replace(/\r/g, '');
    const tmpFile = 'C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_block6_nocr.js';
    fs.writeFileSync(tmpFile, code, 'utf-8');
    
    // Try parsing with vm
    const vm = require('vm');
    try {
      new vm.Script(code);
      console.log('vm.Script: OK');
    } catch(e) {
      console.log('vm.Script ERROR:', e.message);
      // Get line from error
      if (e.stack) {
        const lineMatch = e.stack.match(/<anonymous>:(\d+)/);
        if (lineMatch) {
          console.log('Error at line:', lineMatch[1]);
        }
      }
    }
    
    fs.unlinkSync(tmpFile);
    break;
  }
}
