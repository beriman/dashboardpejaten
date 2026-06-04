const fs = require('fs');
const { execSync } = require('child_process');

const content = fs.readFileSync('H:\\\\My Drive\\\\Work in Progress\\\\08 Laporan Progress Proyek\\\\Dashboard\\\\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html', 'utf-8');

// Extract all inline scripts
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  const code = match[1].replace(/\r/g, '');
  
  const tmpFile = `C:\\\\Users\\\\bim\\\\.openclaw\\\\workspace\\\\deploy\\\\pejaten-dashboard-web\\\\public\\\\_source_block${blockNum}.js`;
  fs.writeFileSync(tmpFile, code, 'utf-8');
  
  try {
    execSync(`node --check "${tmpFile}"`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
    console.log(`Source block ${blockNum}: OK (${code.length} chars)`);
  } catch(e) {
    console.log(`Source block ${blockNum}: ERROR`);
    console.log(e.stderr || e.message);
  }
  
  fs.unlinkSync(tmpFile);
}
