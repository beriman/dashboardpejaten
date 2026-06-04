const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

// Find block 6
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    const lines = code.split('\n');
    
    // Try parsing progressively
    for (let i = 1; i <= Math.min(20, lines.length); i++) {
      const partial = 'async function __test__() {\n' + lines.slice(0, i).join('\n') + '\n}';
      try {
        new Function(partial);
      } catch(e) {
        console.log(`First error at block line ${i}: ${e.message}`);
        console.log(`Line ${i}: ${JSON.stringify(lines[i-1].substring(0, 120))}`);
        // Check for special chars in this line
        for (let j = 0; j < lines[i-1].length; j++) {
          const ch = lines[i-1].charCodeAt(j);
          if (ch > 127 || (ch < 32 && ch !== 10 && ch !== 13 && ch !== 9)) {
            console.log(`  Special char at pos ${j}: U+${ch.toString(16).padStart(4,'0')}`);
          }
        }
        break;
      }
    }
    break;
  }
}
