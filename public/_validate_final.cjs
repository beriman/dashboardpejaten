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
    const tmpFile = 'C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_block6_check.js';
    fs.writeFileSync(tmpFile, code, 'utf-8');
    
    try {
      execSync(`node --check "${tmpFile}"`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
      console.log('node --check: OK');
    } catch(e) {
      console.log('node --check ERROR:');
      console.log(e.stderr || e.message);
    }
    
    fs.unlinkSync(tmpFile);
    break;
  }
}
