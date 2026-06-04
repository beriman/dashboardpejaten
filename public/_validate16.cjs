const fs = require('fs');
const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    
    // Find all occurrences of dataSets key declarations
    const lines = code.split('\n');
    
    // Find "daily:", "weekly:", "monthly:" at the top level of dataSets
    let inDataSets = false;
    let dataSetsDepth = 0;
    let currentKey = null;
    let keyLines = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      if (trimmed.startsWith('const dataSets')) {
        inDataSets = true;
        dataSetsDepth = 0;
      }
      
      if (inDataSets) {
        // Track depth
        for (const ch of line) {
          if (ch === '{') dataSetsDepth++;
          if (ch === '}') dataSetsDepth--;
        }
        
        // Check for top-level keys
        if (dataSetsDepth === 1 && (trimmed.startsWith('daily:') || trimmed.startsWith('weekly:') || trimmed.startsWith('monthly:'))) {
          currentKey = trimmed.split(':')[0];
          keyLines.push({ key: currentKey, line: i + 1, content: trimmed });
        }
        
        if (dataSetsDepth <= 0) {
          inDataSets = false;
          console.log(`dataSets closes at line ${i+1}: ${trimmed}`);
        }
      }
    }
    
    console.log("\nTop-level keys in dataSets:");
    for (const k of keyLines) {
      console.log(`  L${k.line}: ${k.key}: ${k.content.substring(0, 80)}`);
    }
    
    // Now check: for each key, find its closing depth
    console.log("\n=== Checking each key's structure ===");
    for (const k of keyLines) {
      let depth = 0;
      let started = false;
      for (let i = k.line - 1; i < lines.length; i++) {
        const line = lines[i];
        for (const ch of line) {
          if (ch === '{') {
            depth++;
            started = true;
          }
          if (ch === '}') depth--;
        }
        if (started && depth === 0) {
          console.log(`  ${k.key}: opens at L${k.line}, closes at L${i+1}`);
          break;
        }
      }
    }
    
    break;
  }
}
