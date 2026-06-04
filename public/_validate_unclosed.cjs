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
    
    // Find unclosed single-quoted string
    let inString = false;
    let stringChar = null;
    let escaped = false;
    let stringStartLine = -1;
    let stringStartCol = -1;
    
    for (let i = 0; i < lines.length; i++) {
      for (let j = 0; j < lines[i].length; j++) {
        const ch = lines[i][j];
        if (escaped) {
          escaped = false;
          continue;
        }
        if (ch === '\\' && inString) {
          escaped = true;
          continue;
        }
        if ((ch === '"' || ch === "'" || ch === '`') && !inString) {
          inString = true;
          stringChar = ch;
          stringStartLine = i;
          stringStartCol = j;
        } else if (ch === stringChar && inString) {
          inString = false;
          stringChar = null;
        }
      }
    }
    
    if (inString) {
      console.log(`Unclosed string starts at block L${stringStartLine+1}, col ${stringStartCol+1}`);
      console.log('Context:');
      for (let i = stringStartLine; i < Math.min(lines.length, stringStartLine + 5); i++) {
        console.log(`  L${i+1}: ${lines[i]}`);
      }
      
      // Show the specific character
      const line = lines[stringStartLine];
      console.log(`\nChar at col ${stringStartCol}: U+${line.charCodeAt(stringStartCol).toString(16).padStart(4,'0')} ${JSON.stringify(line[stringStartCol])}`);
      console.log(`Surrounding: ${JSON.stringify(line.substring(Math.max(0, stringStartCol-20), stringStartCol+20))}`);
    }
    
    break;
  }
}
