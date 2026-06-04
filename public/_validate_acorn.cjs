const fs = require('fs');
const { parse } = require('node:module');

// Actually, let's just try parsing with different methods
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    
    // Try acorn if available
    try {
      const acorn = require('acorn');
      acorn.parse(code, { ecmaVersion: 2022, sourceType: 'script' });
      console.log('acorn: OK');
    } catch(e) {
      if (e.message.includes('acorn')) {
        console.log('acorn not available, trying manual approach');
      } else {
        console.log('acorn error:', e.message);
        console.log('Position:', e.pos);
        // Find line from position
        const before = code.substring(0, e.pos);
        const lineNum = before.split('\n').length;
        console.log('Approximate line:', lineNum);
      }
    }
    
    break;
  }
}
