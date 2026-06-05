const fs = require('fs');
const html = fs.readFileSync('/h/My Drive/Work in Progress/08 Laporan Progress Proyek/Dashboard/Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html', 'utf8');

// Extract all script blocks with their positions
const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let scripts = [];
let idx = 0;
while ((match = scriptRegex.exec(html)) !== null) {
    idx++;
    const openTag = match[0].match(/<script[^>]*>/i)[0];
    scripts.push({
        index: idx,
        openTag: openTag,
        hasSrc: openTag.includes('src='),
        startPos: match.index,
        innerStart: match.index + openTag.length,
        inner: match[1],
        innerLen: match[1].length,
    });
}

console.log('=== SCRIPT BLOCKS ===');
scripts.forEach(s => {
    console.log('Script ' + s.index + ': ' + (s.hasSrc ? 'EXTERNAL src=' + s.openTag.match(/src="([^"]+)"/)?.[1] : 'INLINE') + ', len=' + s.innerLen);
    if (!s.hasSrc) {
        // Show first 3 lines
        const lines = s.inner.split('\n').slice(0, 3);
        lines.forEach(l => console.log('  > ' + l.substring(0, 100)));
    }
    console.log('');
});

// Find key JS structures in inline scripts
console.log('=== KEY JS STRUCTURES ===');
scripts.forEach(s => {
    if (s.hasSrc) return;
    const inner = s.inner;
    
    // Find const/let/var declarations
    const decls = inner.match(/(?:const|let|var)\s+(\w+)\s*=/g);
    if (decls) {
        console.log('Script ' + s.index + ' declarations:');
        decls.forEach(d => console.log('  ' + d));
    }
    
    // Find function declarations
    const funcs = inner.match(/function\s+(\w+)\s*\(/g);
    if (funcs) {
        console.log('Script ' + s.index + ' functions:');
        funcs.forEach(f => console.log('  ' + f));
    }
});
