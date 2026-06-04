const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    let code = match[1];
    
    // Try different wrapping strategies
    const wrappers = [
      ['IIFE', `(function(){\n${code}\n})`],
      ['Async IIFE', `(async function(){\n${code}\n})`],
      ['Block', `{\n${code}\n}`],
      ['Module', `export default (function(){\n${code}\n})`],
    ];
    
    for (const [name, wrapped] of wrappers) {
      try {
        if (name === 'Module') {
          // Can't use new Function for modules, skip
          continue;
        }
        new Function(wrapped);
        console.log(`${name}: OK`);
      } catch(e) {
        console.log(`${name}: ${e.message}`);
      }
    }
    
    // The real question: does this code run in a browser?
    // In a browser, inline scripts are NOT wrapped - they run at global scope
    // So we need to check if the code is valid at global scope
    
    // Let's try: use vm.Module or just check syntax differently
    // Actually, let's just try to find the issue manually
    
    // Check: is there a line with just '}' that might be wrong?
    const lines = code.split('\n');
    
    // Find all lines that are just closing braces
    const braceOnlyLines = [];
    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim();
      if (trimmed === '}' || trimmed === '});' || trimmed === '},' || trimmed === '};') {
        braceOnlyLines.push(i + 1);
      }
    }
    
    console.log(`\nLines with only closing braces: ${braceOnlyLines.length}`);
    
    // Check for the specific issue: two consecutive }); lines
    for (let i = 0; i < lines.length - 1; i++) {
      const t1 = lines[i].trim();
      const t2 = lines[i+1].trim();
      if ((t1 === '});' || t1 === '}') && (t2 === '});' || t2 === '}' || t2 === '},')) {
        console.log(`Consecutive closing at L${i+1}-L${i+2}: "${t1}" -> "${t2}"`);
      }
    }
    
    break;
  }
}
