const fs = require('fs');
const content = fs.readFileSync('C:\\Users\\bim\\.openclaw\\workspace\\deploy\\pejaten-dashboard-web\\public\\index.html', 'utf-8');

// Extract all script blocks
const scriptRegex = /<script(?!\s+src)[^>]*>([\s\S]*?)<\/script>/g;
let match;
let blockNum = 0;
while ((match = scriptRegex.exec(content)) !== null) {
  blockNum++;
  const code = match[1];
  try {
    // Try to parse as JS
    new Function(code);
    console.log(`Block ${blockNum}: OK (${code.length} chars)`);
  } catch (e) {
    console.log(`Block ${blockNum}: ERROR - ${e.message}`);
    // Find the line number
    const beforeError = content.substring(0, match.index + match[0].indexOf(code));
    const lines = code.split('\n');
    // Try to find the approximate error location
    console.log(`  Block starts at line ${beforeError.split('\n').length}`);
  }
}
