const fs = require('fs');
const { execSync } = require('child_process');

const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

// Extract block 6
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    const code = match[1];
    
    // Write to temp file
    const tmpFile = 'C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_block6.js';
    fs.writeFileSync(tmpFile, code, 'utf-8');
    
    // Try node --check
    try {
      execSync(`node --check "${tmpFile}"`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
      console.log('node --check: OK');
    } catch(e) {
      console.log('node --check ERROR:');
      console.log(e.stderr || e.message);
    }
    
    // Clean up
    fs.unlinkSync(tmpFile);
    break;
  }
}
