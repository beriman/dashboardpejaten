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
    
    // Binary search for the error line
    let lo = 1, hi = lines.length;
    let lastOk = 0;
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      const partial = 'async function __test__() {\n' + lines.slice(0, mid).join('\n') + '\n}';
      try {
        new Function(partial);
        lastOk = mid;
        lo = mid + 1;
      } catch(e) {
        hi = mid - 1;
      }
    }
    
    console.log(`Last OK: line ${lastOk}`);
    console.log(`First error: line ${lastOk + 1}`);
    console.log(`Total lines: ${lines.length}`);
    
    // Show context around error
    const start = Math.max(0, lastOk - 2);
    const end = Math.min(lines.length, lastOk + 5);
    for (let i = start; i < end; i++) {
      const marker = (i === lastOk) ? '>>>' : '   ';
      console.log(`${marker} L${i+1}: ${lines[i].substring(0, 150)}`);
    }
    
    // Check for special characters in the error line
    if (lastOk + 1 <= lines.length) {
      const errLine = lines[lastOk]; // 0-indexed, this is line lastOk+1
      console.log(`\nError line char analysis:`);
      for (let j = 0; j < errLine.length; j++) {
        const ch = errLine.charCodeAt(j);
        if (ch > 127 || (ch < 32 && ch !== 10 && ch !== 9)) {
          console.log(`  Pos ${j}: U+${ch.toString(16).padStart(4,'0')} ${JSON.stringify(errLine[j])}`);
        }
      }
    }
    break;
  }
}
