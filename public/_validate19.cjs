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
    
    // Find all top-level keys in dataSets (depth 1)
    let depth = 0;
    let inDataSets = false;
    const keyRanges = [];
    let currentKey = null;
    let keyStartLine = -1;
    let keyStartDepth = -1;
    
    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim();
      
      if (trimmed.startsWith('const dataSets')) {
        inDataSets = true;
      }
      
      if (!inDataSets) continue;
      
      const o = (lines[i].match(/{/g) || []).length;
      const c = (lines[i].match(/}/g) || []).length;
      
      // Check for top-level key at depth 1
      if (depth === 1 && (trimmed.endsWith(': {') || trimmed.endsWith(': {,') || /^\w+:\s*\{/.test(trimmed))) {
        if (currentKey) {
          // Previous key didn't close properly
          console.log(`WARNING: "${currentKey}" started at L${keyStartLine+1} but new key "${trimmed.split(':')[0]}" found at L${i+1} without closing`);
        }
        currentKey = trimmed.split(':')[0];
        keyStartLine = i;
        keyStartDepth = depth;
        console.log(`Key "${currentKey}" starts at L${i+1}, depth=${depth}`);
      }
      
      depth += o - c;
      
      if (depth <= 0 && inDataSets && i > 5) {
        console.log(`dataSets closes at L${i+1}, depth=${depth}`);
        break;
      }
    }
    
    // Now let's look at the structure more carefully
    // Find "daily:", "weekly:", "monthly:" lines
    console.log("\n=== All dataSets key declarations ===");
    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim();
      if (trimmed.match(/^(daily|weekly|monthly)\s*:/)) {
        console.log(`L${i+1}: ${trimmed.substring(0, 100)}`);
      }
    }
    
    break;
  }
}
