(function() {
  'use strict';

  // ─── Detect mobile / tablet ──────────────────────────────────────
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isMobile = isTouchDevice && window.innerWidth < 1024;

  // ─── State ──────────────────────────────────────────────────────
  let sliceActive = false;
  let layerPanelOpen = false;
  let clipX = 1000, clipY = 1000, clipZ = 1000;
  let clipEnabled = { x: true, y: true, z: true };
  let activeSliceAxis = 'x';
  let sliceSemiTransparent = false;
  let loaded = {};
  let building = 'D';
  let tooltipEl, statusEl, container, scene, camera, controls, renderer;
  let raycaster, mouseVec, isolated = null;
  let origVisible = {};
  let origMaterials = new WeakMap();

  // ─── Helpers ────────────────────────────────────────────────────
  function setStatus(html) { if (statusEl) statusEl.innerHTML = '<strong>Status:</strong> ' + html; }
  function isMobileView() { return window.innerWidth < 1024; }

  // ─── Transform header toolbar into segmented control on mobile ──
  function setupToolbar() {
    const toolbar = document.querySelector('.toolbar');
    if (!toolbar) return;

    if (isMobileView()) {
      toolbar.classList.add('toolbar-mobile');
      // Add collapse button
      if (!document.getElementById('btnToolbarMore')) {
        const moreBtn = document.createElement('button');
        moreBtn.id = 'btnToolbarMore';
        moreBtn.innerHTML = '☰';
        moreBtn.title = 'Tools';
        moreBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          toolbar.classList.toggle('toolbar-expanded');
        });
        toolbar.insertBefore(moreBtn, toolbar.firstChild);
      }
      // Close toolbar when clicking outside
      document.addEventListener('click', (e) => {
        if (!toolbar.contains(e.target)) toolbar.classList.remove('toolbar-expanded');
      });
    } else {
      toolbar.classList.remove('toolbar-expanded');
    }
  }

  // ─── Bottom sheet for slice ──────────────────────────────────────
  function createBottomSheet(id, title, contentHTML) {
    let sheet = document.getElementById(id);
    if (sheet) return sheet;

    sheet = document.createElement('div');
    sheet.id = id;
    sheet.className = 'bs-sheet';

    sheet.innerHTML = `
      <div class="bs-handle" style="display:none"></div>
      <div class="bs-header">
        <div class="bs-title">${title}</div>
        <button class="bs-close" onclick="document.getElementById('${id}').classList.remove('open')">✕</button>
      </div>
      <div class="bs-content">${contentHTML}</div>
    `;

    document.body.appendChild(sheet);
    return sheet;
  }

  function openBottomSheet(id) {
    const sheet = document.getElementById(id);
    if (sheet) sheet.classList.add('open');
  }
  function closeBottomSheet(id) {
    const sheet = document.getElementById(id);
    if (sheet) sheet.classList.remove('open');
  }

  // ─── Fill Slice sheet ────────────────────────────────────────────
  function setupSliceSheet() {
    if (document.getElementById('sliceBottomSheet')) return;
    createBottomSheet('sliceBottomSheet', '✂️ Section Slice', `
      <div class="slice-axis-btns">
        <button data-axis="x" class="active">X</button>
        <button data-axis="y">Y</button>
        <button data-axis="z">Z</button>
      </div>
      <div class="slice-row">
        <label>Posisi</label>
        <input type="range" id="slicePosSlider" min="-50" max="50" step="0.5" value="0">
        <span class="val" id="slicePosVal">0</span>
      </div>
      <div class="slice-row">
        <label>Transparan</label>
        <input type="range" id="sliceOpacitySlider" min="0" max="100" step="5" value="100">
        <span class="val" id="sliceOpacityVal">100%</span>
      </div>
      <div style="margin-top:8px;font-size:11px;color:#94a3b8">
        Y = potongan horizontal (lantai)<br>
        X/Z = potongan vertikal
      </div>
    `);

    const slider = document.getElementById('slicePosSlider');
    const val = document.getElementById('slicePosVal');
    if (slider && val) {
      slider.oninput = () => {
        val.textContent = parseFloat(slider.value).toFixed(1);
        updateClipFromMobileSlider();
      };
    }

    document.querySelectorAll('#sliceBottomSheet [data-axis]').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('#sliceBottomSheet [data-axis]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeSliceAxis = btn.dataset.axis;
      };
    });
  }

  function updateClipFromMobileSlider() {
    const v = parseFloat(document.getElementById('slicePosSlider').value) || 0;
    if (activeSliceAxis === 'x') clipX = v;
    else if (activeSliceAxis === 'y') clipY = v;
    else clipZ = v;
    updateClipping();
  }

  // ─── Fill Layer sheet ────────────────────────────────────────────
  function fillLayerSheet() {
    const sheet = document.getElementById('layerBottomSheet');
    if (!sheet) return;
    const list = sheet.querySelector('#layerList');
    if (!list) return;
    list.innerHTML = '';
    Object.entries(loaded).forEach(([key, model]) => {
      const color = disciplineColors[key] || 0xcccccc;
      const div = document.createElement('div');
      div.className = 'layer-item';
      div.innerHTML = `
        <span class="layer-visible" data-disc="${key}">${model.visible ? '👁️' : '🚫'}</span>
        <div class="layer-dot" style="background:#${color.toString(16).padStart(6,'0')}"></div>
        <span class="layer-name">${legDisc[key] || key}</span>
        <input class="layer-opacity" type="range" min="0" max="100" value="${model.visible ? 100 : 0}" data-disc="${key}">`;
      list.appendChild(div);
    });

    list.querySelectorAll('.layer-visibility-btn').forEach(btn => {
      btn.onclick = () => toggleLayerVisibility(btn.dataset.key, btn);
    });
    list.querySelectorAll('.layer-opacity').forEach(el => {
      el.oninput = () => setLayerOpacity(el.dataset.key, parseInt(el.value) / 100, el.previousElementSibling);
    });
  }

  // ─── Touch gestures ──────────────────────────────────────────────
  let touchStartDist = 0;
  let touchStartFingers = 0;
  let lastTouchX = 0, lastTouchY = 0;
  let touchMoveCount = 0;

  function onTouchStart(e) {
    touchMoveCount = 0;
    if (e.touches.length === 2) {
      // Pinch start
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      touchStartDist = Math.sqrt(dx * dx + dy * dy);
      touchStartFingers = 2;
    } else if (e.touches.length === 1) {
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
      touchStartFingers = 1;
    }
  }

  function onTouchMove(e) {
    e.preventDefault();
    touchMoveCount++;

    if (e.touches.length === 2 && touchStartFingers >= 2) {
      // Pinch zoom
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (touchStartDist > 0 && controls) {
        const scale = touchStartDist / dist;
        // zoom camera
        if (controls.zoom) {
          controls.zoom *= scale;
          controls.update();
        } else {
          camera.position.multiplyScalar(Math.max(0.5, Math.min(2, scale)));
        }
        touchStartDist = dist;
      }
    } else if (e.touches.length === 1 && controls) {
      // Single finger — orbit
      const dx = e.touches[0].clientX - lastTouchX;
      const dy = e.touches[0].clientY - lastTouchY;
      // Use OrbitControls' built-in touch handling
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
    } else if (e.touches.length === 3 && controls) {
      // Three-finger pan
      const dx = e.touches[0].clientX - lastTouchX;
      const dy = e.touches[0].clientY - lastTouchY;
      controls.pan(-dx * 0.5, -dy * 0.5);
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
    }
  }

  function onTouchEnd(e) {
    if (touchMoveCount < 3 && e.changedTouches.length === 1) {
      // Treat as tap — trigger selection
      const touch = e.changedTouches[0];
      handleTap(touch.clientX, touch.clientY);
    }
    touchStartFingers = 0;
    touchStartDist = 0;
  }

  function handleTap(clientX, clientY) {
    if (!container || !raycaster || !camera) return;
    const rect = container.getBoundingClientRect();
    mouseVec.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    mouseVec.y = -((clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouseVec, camera);
    const meshes = [];
    Object.values(loaded).filter(m => m.visible).forEach(m => {
      m.traverse(c => { if (c.isMesh) meshes.push(c); });
    });
    const hits = raycaster.intersectObjects(meshes, false);

    if (hits.length > 0) {
      const obj = hits[0].object;
      if (isolated === obj) {
        // Restore
        Object.values(loaded).forEach(m => m.traverse(c => {
          if (c.isMesh && origVisible[c.uuid] !== undefined) c.visible = origVisible[c.uuid];
        }));
        isolated = null;
        tooltipEl.style.display = 'none';
        setStatus('Semua objek ditampilkan.');
      } else {
        // Isolate
        if (!isolated) {
          Object.values(loaded).forEach(m => m.traverse(c => {
            if (c.isMesh) origVisible[c.uuid] = c.visible;
          }));
        }
        Object.values(loaded).forEach(m => m.traverse(c => {
          if (c.isMesh) c.visible = false;
        }));
        obj.visible = true;
        isolated = obj;
        tooltipEl.style.display = 'none';

        // Show bottom sheet with object info
        const info = document.createElement('div');
        info.innerHTML = `<div class="tt-name">${obj.name || 'Element'}</div>
          <div class="tt-attr">Model: ${obj.parent?.name || building}</div>`;
        showObjectSheet(info);
        setStatus(`Isolated: ${obj.name || 'Element'} — tap lagi restore.`);
      }
    } else if (isolated) {
      Object.values(loaded).forEach(m => m.traverse(c => {
        if (c.isMesh && origVisible[c.uuid] !== undefined) c.visible = origVisible[c.uuid];
      }));
      isolated = null;
      tooltipEl.style.display = 'none';
      setStatus('Semua objek ditampilkan.');
    }
  }

  function showObjectSheet(infoEl) {
    let sheet = document.getElementById('objectInfoSheet');
    if (!sheet) {
      sheet = createBottomSheet('objectInfoSheet', '📋 Object Info', '<div id="objectInfoContent"></div>');
    }
    const content = sheet.querySelector('#objectInfoContent');
    if (content) content.innerHTML = '';
    if (content) content.appendChild(infoEl);
    openBottomSheet('objectInfoSheet');
  }

  // ─── Inject FAB (floating action button) on mobile ───────────────
  function injectFAB() {
    if (!isMobileView()) return;
    if (document.getElementById('mobileFAB')) return;

    const fab = document.createElement('div');
    fab.id = 'mobileFAB';
    fab.innerHTML = '🔧';
    fab.onclick = () => {
      document.getElementById('fabMenu').classList.toggle('open');
    };

    const menu = document.createElement('div');
    menu.id = 'fabMenu';
    menu.innerHTML = `
      <div class="fab-menu-item" onclick="document.getElementById('fabMenu').classList.remove('open');openBottomSheet('sliceBottomSheet');">✂️ Slice</div>
      <div class="fab-menu-item" onclick="document.getElementById('fabMenu').classList.remove('open');fillLayerSheet();openBottomSheet('layerBottomSheet');">🏗️ Layer</div>
      <div class="fab-menu-item" onclick="document.getElementById('fabMenu').classList.remove('open');document.getElementById('showAll')?.click();">📦 All</div>
      <div class="fab-menu-item" onclick="document.getElementById('fabMenu').classList.remove('open');document.getElementById('btnReset')?.click();">🔄 Reset</div>
      <div class="fab-menu-item" onclick="document.getElementById('fabMenu').classList.remove('open');document.getElementById('btnScreenshot')?.click();">📷 Capture</div>
    `;

    document.body.appendChild(fab);
    document.body.appendChild(menu);

    // Close menu on outside tap
    document.addEventListener('click', (e) => {
      if (!fab.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('open');
      }
    });
  }

  // ─── Observe when IFC models are loaded ──────────────────────────
  const origLoadDiscipline = window.loadDiscipline;
  window.loadDiscipline = function(discipline) {
    origLoadDiscipline(discipline).then(() => {
      if (isMobileView()) {
        fillLayerSheet();
      }
    });
  };

  // ─── Expose updateClipping ───────────────────────────────────────
  window.updateClipping = function() {
    [clipX, clipY, clipZ].forEach((v, i) => {
      if (window.planes && window.planes[i]) window.planes[i].constant = v;
    });
    const active = [];
    if (clipEnabled.x && window.planes) active.push(window.planes[0]);
    if (clipEnabled.y && window.planes) active.push(window.planes[1]);
    if (clipEnabled.z && window.planes) active.push(window.planes[2]);
    if (window.scene) {
      window.scene.traverse(obj => {
        if (obj.material) {
          obj.material.clippingPlanes = active;
          obj.material.clipShadows = true;
          obj.material.needsUpdate = true;
        }
      });
    }
  };

  // ─── Init ────────────────────────────────────────────────────────
  function initMobileUI() {
    // Grab references from the viewer's global scope
    scene = window.scene;
    camera = window.camera;
    controls = window.controls;
    renderer = window.renderer;
    container = document.getElementById('viewer');
    tooltipEl = document.getElementById('tooltip');
    statusEl = document.getElementById('status');
    raycaster = window.raycaster;
    mouseVec = window.mouseVec;
    loaded = window.loaded || {};
    building = window.building || 'D';
    origVisible = window.origVisible || {};
    origMaterials = window.origMaterials || new WeakMap();
    // discipline colors
    window.disciplineColors = window.disciplineColors || { STR: 0xef4444, ARS: 0x3b82f6, INT: 0x22c55e, MEP: 0xf59e0b };
    window.legDisc = window.legDisc || { STR: 'Struktur', ARS: 'Arsitektur', INT: 'Interior', MEP: 'MEP' };
    // Expose for mobile sheet
    window.toggleLayerVisibility = function(key, btn) {
      if (!loaded[key]) return;
      loaded[key].visible = !loaded[key].visible;
      btn.textContent = loaded[key].visible ? '👁️' : '🚫';
    };
    window.setLayerOpacity = function(key, opacity, btn) {
      if (!loaded[key]) return;
      loaded[key].visible = opacity > 0;
      if (btn) btn.textContent = opacity > 0 ? '👁️' : '🚫';
      loaded[key].traverse(child => {
        if (child.material) {
          const mats = Array.isArray(child.material) ? child.material : [child.material];
          mats.forEach(mat => {
            if (opacity > 0.5) { mat.opacity = 1; mat.transparent = false; }
            else { mat.opacity = opacity; mat.transparent = true; }
          });
        }
      });
    };

    // ─── 1. Toolbar ─────────────────────────────────────────────────
    setupToolbar();

    // ─── 2. Bottom sheets ───────────────────────────────────────────
    setupSliceSheet();
    createBottomSheet('layerBottomSheet', '🏗️ Layers', '<div id="layerList"></div>');
    fillLayerSheet();

    // ─── 3. FAB ─────────────────────────────────────────────────────
    injectFAB();

    // ─── 4. Touch gestures ──────────────────────────────────────────
    if (container) {
      container.addEventListener('touchstart', onTouchStart, { passive: false });
      container.addEventListener('touchmove', onTouchMove, { passive: false });
      container.addEventListener('touchend', onTouchEnd, { passive: false });
    }

    // ─── 5. Keyboard shortcuts ──────────────────────────────────────
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeBottomSheet('sliceBottomSheet');
        closeBottomSheet('layerBottomSheet');
        closeBottomSheet('objectInfoSheet');
      }
      if (e.key === 's' || e.key === 'S') {
        document.getElementById('btnSlice')?.click();
      }
      if (e.key === 'l' || e.key === 'L') {
        document.getElementById('btnLayer')?.click();
      }
    });

    // ─── 6. Responsive: re-layout on resize ─────────────────────────
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        setupToolbar();
        if (isMobileView()) {
          injectFAB();
          document.body.classList.add('is-mobile');
        } else {
          document.body.classList.remove('is-mobile');
          const fab = document.getElementById('mobileFAB');
          const menu = document.getElementById('fabMenu');
          if (fab) fab.remove();
          if (menu) menu.remove();
        }
      }, 200);
    });

    // ─── 7. Initial state ───────────────────────────────────────────
    if (isMobileView()) {
      document.body.classList.add('is-mobile');
      // Auto-open slice hint on first load
      setStatus('💡 Tap objek = isolasi. 2 jari = zoom. 3 jari = pan. Toolbar > untuk tools.');
    }

    console.log('[MobileUI] Initialized — mobile:', isMobileView(), 'touch:', isTouchDevice);
  }

  // ─── Auto-run on dom ready ────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      // Wait for the three.js boot script to finish
      setTimeout(initMobileUI, 300);
    });
  } else {
    setTimeout(initMobileUI, 300);
  }
})();
