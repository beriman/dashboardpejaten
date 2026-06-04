const fs = require('fs');
const { execSync } = require('child_process');

const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    const lines = code.split('\n');
    
    // The error is at block6 line 209 = absolute line (block6_start + 208)
    // Let's check what's really there
    console.log("Block 6 line 209:");
    console.log(JSON.stringify(lines[208]));
    
    // Check lines around it
    for (let i = 206; i < 212; i++) {
      console.log(`L${i+1}: ${JSON.stringify(lines[i])}`);
    }
    
    // The issue: line 209 is `    };` which closes dataSets
    // But node --check says it's unexpected
    // This means the parser already thinks dataSets is closed by line 207's `]`
    // So `}` on line 209 is extra, making `;` unexpected
    
    // Wait - `]` closes an array. Then `}` closes the object. That's fine.
    // Unless... the `}` on line 206 already closed the object
    // and `]` on line 207 is closing something else
    
    // Let me trace from the start of dataSets
    console.log("\n=== Tracing dataSets structure ===");
    let depth = 0;
    let inDataSets = false;
    for (let i = 0; i < 215; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      if (trimmed.startsWith('const dataSets')) {
        inDataSets = true;
        console.log(`L${i+1} depth=${depth}: ${trimmed}`);
      }
      
      if (inDataSets) {
        let lineDepth = depth;
        for (const ch of line) {
          if (ch === '{') { depth++; lineDepth++; }
          if (ch === '}') { depth--; lineDepth--; }
        }
        if (i >= 200) {
          console.log(`L${i+1} depth=${depth} (lineΔ${lineDepth >= 0 ? '+' : ''}${lineDepth}): ${trimmed.substring(0, 80)}`);
        }
        if (depth <= 0 && inDataSets && i > 5) {
          console.log(`  *** dataSets closes at L${i+1} ***`);
          inDataSets = false;
        }
      }
    }
    
    break;
  }
}
