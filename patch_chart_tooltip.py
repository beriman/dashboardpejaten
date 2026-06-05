"""Patch dashboard chart: sparse x-axis labels + hover tooltip."""
import re, shutil

HTML_PATH = r'H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html'
html = open(HTML_PATH, encoding='utf-8', errors='ignore').read()

# 1. Replace the xLabels line with sparse labels (show every 5th + first + last)
old_xlabels = 'const xLabels = labels.map((lab,i) => `<text x="${x(i)}" y="${h-16}" font-size="11" fill="#9aa8bc" text-anchor="middle">${lab}</text>`).join(\'\');'

new_xlabels = '''const xLabels = labels.map((lab,i) => {
        const show = (i === 0) || (i === labels.length - 1) || (i % 5 === 0);
        if (!show) return '';
        return `<text x="${x(i)}" y="${h-16}" font-size="10" fill="#9aa8bc" text-anchor="middle">${lab}</text>`;
      }).join('');'''

if old_xlabels in html:
    html = html.replace(old_xlabels, new_xlabels)
    print("✅ xLabels: sparse labels (every 5th + first + last)")
else:
    print("❌ xLabels pattern not found!")

# 2. Add tooltip circles after the existing circles in the SVG
# Find the pattern: ${circles(real, '#22c55e')} followed by ${xLabels}
# We need to add interactive tooltip circles between the data circles and xLabels

old_svg_end = '''              ${circles(real, '#22c55e')}
              ${xLabels}'''

new_svg_end = '''              ${circles(real, '#22c55e')}
              ${xLabels}
              ${tooltipCircles(labels, plan, real)}'''

if old_svg_end in html:
    html = html.replace(old_svg_end, new_svg_end)
    print("✅ Added tooltipCircles call")
else:
    print("❌ SVG end pattern not found!")

# 3. Add the tooltipCircles function and tooltip CSS/HTML
# Insert the function right before the makeChartSVG closing brace
# Find the return statement of makeChartSVG and insert before it

tooltip_js = '''
    const tooltipCircles = (labels, plan, real) => {
      return labels.map((lab, i) => {
        const cx = x(i);
        const cyPlan = y(plan[i]);
        const cyReal = y(real[i]);
        const valPlan = plan[i] !== null && plan[i] !== undefined ? plan[i].toFixed(2) + '%' : '-';
        const valReal = real[i] !== null && real[i] !== undefined ? real[i].toFixed(2) + '%' : '-';
        const tip = `${lab}\\nRencana: ${valPlan}\\nRealisasi: ${valReal}`;
        return `<g class="tt-group">
          <line x1="${cx}" y1="${mt}" x2="${cx}" y2="${h-mb}" class="tt-line" />
          <circle cx="${cx}" cy="${cyPlan}" r="8" class="tt-dot" data-tip="${tip}" />
          <circle cx="${cx}" cy="${cyReal}" r="8" class="tt-dot" data-tip="${tip}" />
        </g>`;
      }).join('');
    };
'''

# Insert tooltipCircles function before makeChartSVG function
old_func = 'function makeChartSVG(labels, plan, real, title, subtitle) {'
if old_func in html:
    html = html.replace(old_func, tooltip_js + '    ' + old_func)
    print("✅ Added tooltipCircles function")
else:
    print("❌ makeChartSVG function not found!")

# 4. Add tooltip CSS + HTML container + JS event handler
# Find a good place to inject CSS - look for existing chart CSS
tooltip_css = '''
    <style>
    .chart-wrap { position: relative; }
    .tt-group { opacity: 0; transition: opacity 0.15s; cursor: pointer; }
    .chart-wrap:hover .tt-group { opacity: 1; }
    .tt-line { stroke: rgba(255,255,255,0.15); stroke-width: 1; stroke-dasharray: 3 3; pointer-events: none; }
    .tt-dot { fill: transparent; stroke: transparent; }
    .tt-group:hover .tt-line { stroke: rgba(255,255,255,0.5); stroke-width: 1.5; stroke-dasharray: none; }
    .tt-group:hover .tt-dot { fill: rgba(255,255,255,0.15); stroke: rgba(255,255,255,0.4); stroke-width: 1; }
    #chart-tooltip {
      position: fixed; z-index: 9999; pointer-events: none;
      background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(148,163,184,0.25);
      border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #e2e8f0;
      white-space: pre-line; line-height: 1.6; box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      display: none; max-width: 220px;
    }
    #chart-tooltip .tt-date { font-weight: 700; color: #38bdf8; display: block; margin-bottom: 4px; }
    #chart-tooltip .tt-row { display: flex; justify-content: space-between; gap: 12px; }
    #chart-tooltip .tt-label { color: #94a3b8; }
    #chart-tooltip .tt-val { font-weight: 600; }
    #chart-tooltip .tt-plan { color: #f59e0b; }
    #chart-tooltip .tt-real { color: #22c55e; }
    </style>
'''

# Add tooltip HTML container
tooltip_html = '<div id="chart-tooltip"></div>\n'

# Inject CSS before </head>
if '</head>' in html and tooltip_css.strip() not in html:
    html = html.replace('</head>', tooltip_css + '  </head>', 1)
    print("✅ Added tooltip CSS")
else:
    print("⚠️ CSS already present or </head> not found")

# Inject HTML container before </body>
if '</body>' in html and 'chart-tooltip' not in html:
    html = html.replace('</body>', tooltip_html + '</body>', 1)
    print("✅ Added tooltip HTML container")
else:
    print("⚠️ HTML container already present or </body> not found")

# 5. Add tooltip JS event handler at the end of the last script
tooltip_handler = '''
<script>
(function() {
  var tip = document.getElementById('chart-tooltip');
  if (!tip) return;
  var showTip = function(e) {
    var g = e.target.closest('.tt-group');
    if (!g) return;
    var dot = g.querySelector('.tt-dot');
    if (!dot) return;
    var raw = dot.getAttribute('data-tip') || '';
    var parts = raw.split('\\n');
    var date = parts[0] || '';
    var plan = (parts[1] || '').replace('Rencana: ', '');
    var real = (parts[2] || '').replace('Realisasi: ', '');
    tip.innerHTML = '<span class="tt-date">' + date + '</span>'
      + '<div class="tt-row"><span class="tt-label">Rencana</span><span class="tt-val tt-plan">' + plan + '</span></div>'
      + '<div class="tt-row"><span class="tt-label">Realisasi</span><span class="tt-val tt-real">' + real + '</span></div>';
    tip.style.display = 'block';
    var rect = dot.getBoundingClientRect();
    var tipW = 180;
    var left = rect.left + rect.width / 2 - tipW / 2;
    left = Math.max(8, Math.min(window.innerWidth - tipW - 8, left));
    tip.style.left = left + 'px';
    tip.style.top = (rect.top - tip.offsetHeight - 10) + 'px';
  };
  var hideTip = function() { tip.style.display = 'none'; };
  document.addEventListener('mouseover', function(e) {
    if (e.target.closest('.tt-group')) showTip(e);
  });
  document.addEventListener('mouseout', function(e) {
    if (e.target.closest('.tt-group')) hideTip();
  });
  document.addEventListener('mousemove', function(e) {
    if (e.target.closest('.tt-group')) showTip(e);
  });
})();
</script>
'''

if '</body>' in html and 'chart-tooltip' not in html.split('</body>')[0]:
    # Already added HTML, now add JS
    pass

# Add the script before </body>
if tooltip_handler.strip() not in html:
    html = html.replace('</body>', tooltip_handler + '</body>', 1)
    print("✅ Added tooltip JS handler")
else:
    print("⚠️ Tooltip JS already present")

# Backup and write
backup_path = HTML_PATH + '.backup_tooltip'
shutil.copy2(HTML_PATH, backup_path)
print(f"\nBackup: {backup_path}")

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML updated!")
