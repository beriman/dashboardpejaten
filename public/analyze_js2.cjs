const fs = require('fs');
const html = fs.readFileSync('public/dash_src.html', 'utf8');

// Extract all script blocks
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
        inner: match[1],
        innerLen: match[1].length,
    });
}

console.log('=== SCRIPT BLOCKS ===');
scripts.forEach(s => {
    const srcMatch = s.openTag.match(/src="([^"]+)"/);
    console.log('Script ' + s.index + ': ' + (s.hasSrc ? 'EXTERNAL src=' + srcMatch?.[1] : 'INLINE') + ', len=' + s.innerLen);
    if (!s.hasSrc) {
        const lines = s.inner.split('\n').slice(0, 3);
        lines.forEach(l => console.log('  > ' + l.substring(0, 100)));
    }
    console.log('');
});

// Deep dive into inline scripts - find all declarations
console.log('=== KEY JS DECLARATIONS ===');
scripts.forEach(s => {
    if (s.hasSrc) return;
    const inner = s.inner;
    
    // Top-level const/let/var
    const decls = inner.match(/(?:const|let|var)\s+(\w+)\s*[=;]/g);
    if (decls) {
        console.log('Script ' + s.index + ' top-level declarations:');
        [...new Set(decls)].forEach(d => console.log('  ' + d.trim()));
    }
    
    // Function declarations
    const funcs = inner.match(/(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]*)\s*=>)/g);
    if (funcs) {
        console.log('Script ' + s.index + ' functions:');
        funcs.forEach(f => console.log('  ' + f.trim().substring(0, 80)));
    }
    console.log('');
});

// Find dataSets structure
console.log('=== DATASETS STRUCTURE ===');
const s6 = scripts.find(s => !s.hasSrc && s.innerLen > 100000);
if (s6) {
    const inner = s6.inner;
    // Find dataSets opening
    const dsMatch = inner.match(/const\s+dataSets\s*=\s*\{/);
    if (dsMatch) {
        console.log('dataSets found at offset:', dsMatch.index);
        // Show structure keys
        const keys = inner.match(/(?:daily|weekly|monthly|buildings|projectName|sourceDate|mode)\s*:/g);
        if (keys) {
            console.log('Keys found:', [...new Set(keys)]);
        }
    }
    
    // Find renderDashboard or similar main render function
    const renderMatch = inner.match(/(?:function\s+render|const\s+render\w*\s*=\s*\(\)|const\s+render\w*\s*=\s*\([^)]*\)\s*=>)/g);
    if (renderMatch) {
        console.log('Render functions:', renderMatch);
    }
    
    // Find IIFE
    const iifeMatch = inner.match(/\(function\(\)\s*\{/g);
    console.log('IIFE count:', iifeMatch ? iifeMatch.length : 0);
    
    // Find DOMContentLoaded or ready state
    const readyMatch = inner.match(/(?:DOMContentLoaded|document\.readyState|window\.onload|requestAnimationFrame)/g);
    if (readyMatch) {
        console.log('Ready handlers:', [...new Set(readyMatch)]);
    }
}
