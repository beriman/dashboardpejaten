const fs = require('fs');
const content = fs.readFileSync('H:\\\\My Drive\\\\Work in Progress\\\\08 Laporan Progress Proyek\\\\Dashboard\\\\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html', 'utf-8');

// Find the chat handler in the source
const idx = content.indexOf("header-chat-btn");
if (idx >= 0) {
  console.log("Found header-chat-btn at char offset:", idx);
  console.log("Context (500 chars before, 500 after):");
  const start = Math.max(0, idx - 200);
  const end = Math.min(content.length, idx + 800);
  console.log(content.substring(start, end));
}
