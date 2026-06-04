const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    const lines = code.split('\n');
    
    // Line 209 is the error. Show L200-L220
    console.log("=== Block 6 lines 200-220 ===");
    for (let i = 199; i < Math.min(lines.length, 220); i++) {
      const marker = (i === 208) ? '>>>' : '   ';
      console.log(`${marker} L${i+1}: ${lines[i]}`);
    }
    
    // Now: trace the { } balance from line 1 to 209
    let depth = 0;
    for (let i = 0; i < 209; i++) {
      for (const ch of lines[i]) {
        if (ch === '{') depth++;
        if (ch === '}') depth--;
      }
    }
    console.log(`\nDepth at line 209: ${depth}`);
    
    // What about from line 210 onwards?
    let endDepth = 0;
    for (let i = 209; i < lines.length; i++) {
      for (const ch of lines[i]) {
        if (ch === '{') endDepth++;
        if (ch === '}') endDepth--;
      }
    }
    console.log(`Depth change from line 210 to end: ${endDepth}`);
    console.log(`Total depth change: ${depth + endDepth}`);
    
    break;
  }
}
