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
    
    // Remove all \r
    const codeClean = code.replace(/\r/g, '');
    
    const tmpFile = 'C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_block6_clean.js';
    fs.writeFileSync(tmpFile, codeClean, 'utf-8');
    
    try {
      execSync(`node --check "${tmpFile}"`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
      console.log('Without CR: OK');
    } catch(e) {
      console.log('Without CR ERROR:');
      console.log(e.stderr || e.message);
    }
    
    // Also try: just lines 200-220
    const lines = codeClean.split('\n');
    const snippet = lines.slice(199, 220).join('\n');
    console.log('\nLines 200-220:');
    console.log(snippet);
    
    fs.unlinkSync(tmpFile);
    break;
  }
}
