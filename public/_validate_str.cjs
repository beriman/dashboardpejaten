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
    
    // Line 209 (0-indexed: 208)
    const line209 = lines[208];
    console.log('Line 209 raw:', JSON.stringify(line209));
    console.log('Line 209 char codes:');
    for (let i = 0; i < line209.length; i++) {
      console.log(`  [${i}] U+${line209.charCodeAt(i).toString(16).padStart(4,'0')} ${JSON.stringify(line209[i])}`);
    }
    
    // Check line 208 and 210 too
    console.log('\nLine 208 raw:', JSON.stringify(lines[207]));
    console.log('Line 210 raw:', JSON.stringify(lines[209]));
    
    // The issue might be that line 209 is `    };` but the parser expects `    }` 
    // because the `;` is unexpected after `}` in this context
    // Wait... `};` is valid JS. `}` closes an object literal, `;` ends the statement.
    
    // Unless... the `}` is being parsed as something else
    // Let me check: is there a string literal that's not closed?
    
    // Check for unclosed strings
    let inString = false;
    let stringChar = null;
    let escaped = false;
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
        } else if (ch === stringChar && inString) {
          inString = false;
          stringChar = null;
        }
      }
    }
    console.log(`\nString state at end: inString=${inString}, stringChar=${stringChar}`);
    if (inString) {
      console.log('UNCLOSED STRING DETECTED!');
    }
    
    break;
  }
}
