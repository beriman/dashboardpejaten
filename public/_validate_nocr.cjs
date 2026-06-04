const fs = require('fs');
const { execSync } = require('child_process');

const content = fs.readFileSync('C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\index.html', 'utf-8');

const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  if (blockNum === 6) {
    // Remove \r
    const code = match[1].replace(/\r/g, '');
    
    const tmpFile = 'C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_block6_test.js';
    fs.writeFileSync(tmpFile, code, 'utf-8');
    
    try {
      execSync(`node --check "${tmpFile}"`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
      console.log('node --check (no CR): OK');
    } catch(e) {
      console.log('node --check (no CR) ERROR:');
      console.log(e.stderr || e.message);
      
      // Extract line number from error
      const lineMatch = (e.stderr || e.message).match(/:(\d+)/);
      if (lineMatch) {
        const errLine = parseInt(lineMatch[1]);
        const lines = code.split('\n');
        console.log(`\nError at line ${errLine}:`);
        for (let i = Math.max(0, errLine-3); i < Math.min(lines.length, errLine+2); i++) {
          const marker = (i === errLine-1) ? '>>>' : '   ';
          console.log(`${marker} L${i+1}: ${lines[i]}`);
        }
      }
    }
    
    fs.unlinkSync(tmpFile);
    break;
  }
}
