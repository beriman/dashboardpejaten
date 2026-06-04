const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    let code = match[1];
    if (code.charCodeAt(0) === 0xFEFF) code = code.slice(1);
    
    // Track depth and find where the unclosed block starts
    let depth = 0;
    const lines = code.split('\n');
    let maxDepth = 0;
    let maxDepthLine = 0;
    
    for (let i = 0; i < lines.length; i++) {
      for (let j = 0; j < lines[i].length; j++) {
        if (lines[i][j] === '{') {
          depth++;
          if (depth > maxDepth) {
            maxDepth = depth;
            maxDepthLine = i;
          }
        }
        if (lines[i][j] === '}') {
          depth--;
        }
      }
    }
    
    console.log(`Final depth: ${depth} (should be 0)`);
    console.log(`Max depth: ${maxDepth} at line ${maxDepthLine + 1}`);
    
    // The issue: final depth is 1, meaning one { is never closed
    // This is likely a missing } somewhere near functions
    
    // Let's check: find all function declarations and IIFEs
    // and verify they're properly closed
    
    // Actually, let's just check the last 50 lines for missing }
    console.log("\n=== Last 50 lines ===");
    for (let i = Math.max(0, lines.length - 50); i < lines.length; i++) {
      console.log(`L${i+1}: ${lines[i]}`);
    }
    
    // Check: is there a function or IIFE that starts but doesn't end?
    // Look for patterns like "function(" or "=> {" near the end
    console.log("\n=== Searching for unclosed blocks ===");
    depth = 0;
    let lastOpenLine = -1;
    for (let i = 0; i < lines.length; i++) {
      const o = (lines[i].match(/{/g) || []).length;
      const c = (lines[i].match(/}/g) || []).length;
      depth += o - c;
      
      if (o > 0 && depth > 0) {
        lastOpenLine = i;
      }
    }
    
    // Find lines that open a block near the end
    console.log("\n=== Lines with { near the end ===");
    for (let i = lines.length - 100; i < lines.length; i++) {
      if (lines[i].includes('{')) {
        console.log(`L${i+1} (depth contribution): ${lines[i].trim().substring(0, 100)}`);
      }
    }
    
    break;
  }
}
