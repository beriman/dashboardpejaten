const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

// Get block 6
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    // Remove BOM if present
    let code = match[1];
    if (code.charCodeAt(0) === 0xFEFF) code = code.slice(1);
    
    // The code uses top-level const, let, var - wrap in block scope
    const wrapped = '"use strict";\n{\n' + code + '\n}';
    
    try {
      new Function(wrapped);
      console.log("Block 6: PARSES OK");
    } catch(e) {
      console.log("Block 6 PARSE ERROR:", e.message);
      
      // If it says "Unexpected token ';'" that usually means 
      // there's an extra } somewhere that closes a block prematurely
      // and then the remaining code has a stray ;
      
      // Let's check: count all braces
      let depth = 0;
      const lines = code.split('\n');
      for (let i = 0; i < lines.length; i++) {
        for (let j = 0; j < lines[i].length; j++) {
          if (lines[i][j] === '{') depth++;
          if (lines[i][j] === '}') depth--;
          if (depth < 0) {
            console.log(`Negative depth at line ${i+1}, col ${j+1}`);
            console.log(`Line: ${lines[i]}`);
            // Show context
            for (let k = Math.max(0, i-3); k <= Math.min(lines.length-1, i+2); k++) {
              console.log(`  L${k+1}: ${lines[k]}`);
            }
            break;
          }
        }
        if (depth < 0) break;
      }
      console.log(`Final depth: ${depth}`);
    }
    break;
  }
}
