import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { IFCLoader } from 'web-ifc-three/IFCLoader.js';

const params = new URLSearchParams(location.search);
const building = (params.get('building') || 'D').toUpperCase();
const disciplineParam = (params.get('discipline') || 'STR').toUpperCase();
const labels = { B: 'Gedung B', D: 'Gedung D', K: 'Gedung K' };
document.getElementById('buildingLabel').textContent = labels[building] || `Gedung ${building}`;

const modelMap = { D: { STR: '/models/Gedung D/IFC/STR/STR D.ifc' } };
const status = document.getElementById('status');
const container = document.getElementById('viewer');
const contextMenu = document.getElementById('contextMenu');
function setStatus(html) { status.innerHTML = `<strong>Status:</strong> ${html}`; }
setStatus('library viewer siap, membuat scene 3D...');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x08111f);
const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000000);
camera.position.set(35, 28, 35);
const renderer = new THREE.WebGLRenderer({ antialias: true, logarithmicDepthBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.localClippingEnabled = true;
container.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
scene.add(new THREE.AmbientLight(0xffffff, 0.85));
const dir = new THREE.DirectionalLight(0xffffff, 1.4);
dir.position.set(50, 80, 30);
scene.add(dir);
scene.add(new THREE.GridHelper(120, 60, 0x2b6cb0, 0x1e293b));
scene.add(new THREE.AxesHelper(12));

const clippingPlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
let sectionOn = false;
const loaded = {};
let activeDiscipline = disciplineParam;
let selected = null;

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const highlightMaterial = new THREE.MeshLambertMaterial({ color: 0xffc107, transparent: true, opacity: 0.75, depthTest: false });
const loader = new IFCLoader();
loader.ifcManager.setWasmPath('/vendor/web-ifc/', true);

const visibleSubsetId = discipline => `VISIBLE_${discipline}`;
const selectSubsetId = discipline => `SELECT_${discipline}`;

function uniqueExpressIds(model) {
  const attr = model.geometry?.attributes?.expressID;
  if (!attr) return [];
  return [...new Set(Array.from(attr.array).filter(v => Number.isFinite(v) && v >= 0))];
}

function visibleMesh(entry) {
  return loader.ifcManager.getSubset(entry.model.modelID, undefined, visibleSubsetId(entry.discipline));
}

function applyClipping(object) {
  object.traverse(child => {
    if (child.material) {
      child.material.clippingPlanes = sectionOn ? [clippingPlane] : [];
      child.material.clipShadows = true;
      child.material.side = THREE.DoubleSide;
    }
  });
}

function rebuildVisibleSubset(entry, ids = [...entry.visibleIds]) {
  try { loader.ifcManager.removeSubset(entry.model.modelID, undefined, visibleSubsetId(entry.discipline)); } catch { /* already removed */ }
  entry.visibleIds = new Set(ids);
  try {
    const subset = loader.ifcManager.createSubset({
      modelID: entry.model.modelID,
      ids,
      scene,
      removePrevious: true,
      customID: visibleSubsetId(entry.discipline)
    });
    if (!subset) throw new Error('createSubset returned null/undefined');
    subset.name = `${entry.discipline}-visible-subset`;
    subset.visible = entry.model.visible;
    applyClipping(subset);
    return subset;
  } catch (e) {
    console.warn('rebuildVisibleSubset failed, showing raw model as fallback:', e.message);
    entry.model.visible = entry.model.visible !== false;
    applyClipping(entry.model);
    return entry.model;
  }
}

function clearSelection() {
  if (!selected?.entry) return;
  loader.ifcManager.removeSubset(selected.entry.model.modelID, highlightMaterial, selectSubsetId(selected.entry.discipline));
  selected = null;
}

async function elementLabel(entry, expressID) {
  try {
    const props = await loader.ifcManager.getItemProperties(entry.model.modelID, expressID, false);
    const name = props?.Name?.value || props?.Name || props?.GlobalId?.value || '';
    const type = props?.type || props?.ObjectType?.value || '';
    return `${entry.discipline} #${expressID}${name ? ` - ${name}` : ''}${type ? ` (${type})` : ''}`;
  } catch {
    return `${entry.discipline} #${expressID}`;
  }
}

function frameObject(object) {
  const box = new THREE.Box3().setFromObject(object);
  if (box.isEmpty()) { setStatus('IFC terbaca, tapi bounding box kosong. Cek export IFC/model visibility.'); return; }
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  controls.target.copy(center);
  const maxDim = Math.max(size.x, size.y, size.z) || 20;
  const dist = maxDim * 1.4;
  camera.position.set(center.x + dist, center.y + dist * 0.7, center.z + dist);
  camera.near = Math.max(maxDim / 1000, 0.1);
  camera.far = maxDim * 1000;
  camera.updateProjectionMatrix();
  controls.update();
}

async function loadDiscipline(discipline) {
  activeDiscipline = discipline;
  const url = modelMap[building]?.[discipline];
  if (!url) { setStatus(`${labels[building] || building} - ${discipline} belum ada file IFC di paket dashboard. Upload/export IFC dulu lalu publish ulang.`); return; }
  if (loaded[discipline]) {
    clearSelection();
    Object.values(loaded).forEach(e => { e.model.visible = false; const s = visibleMesh(e); if (s) s.visible = false; });
    loaded[discipline].model.visible = true;
    const subset = visibleMesh(loaded[discipline]);
    if (subset) subset.visible = true;
    frameObject(subset || loaded[discipline].model);
    setStatus(`Menampilkan ${labels[building]} - ${discipline}. Klik elemen untuk select, klik kanan untuk Hide/Isolate.`);
    return;
  }
  setStatus(`Memuat ${discipline}: ${url}`);
  try {
    const model = await loader.loadAsync(url);
    model.name = `${building}-${discipline}`;
    applyClipping(model);
    scene.add(model);
    let ids = [];
    try { ids = uniqueExpressIds(model); } catch (e) { console.warn('uniqueExpressIds failed:', e.message); }
    const entry = { discipline, model, allIds: ids, visibleIds: new Set(ids) };
    loaded[discipline] = entry;
    Object.values(loaded).forEach(e => { e.model.visible = false; const s = visibleMesh(e); if (s) s.visible = false; });
    model.visible = true;
    let subset;
    try {
      subset = rebuildVisibleSubset(entry, ids);
    } catch (e) {
      console.warn('rebuildVisibleSubset threw, using model as fallback:', e.message);
      model.visible = true;
      subset = model;
    }
    model.visible = false;
    if (subset) subset.visible = true;
    frameObject(subset);
    setStatus(`Berhasil memuat ${labels[building]} - ${discipline}. Klik elemen untuk select, klik kanan untuk Hide/Isolate.`);
  } catch (err) {
    console.error(err);
    setStatus(`Gagal memuat IFC ${discipline}. Detail: ${err?.message || err}`);
  }
}

async function showAll() {
  clearSelection();
  const entries = Object.keys(modelMap[building] || {});
  if (!entries.length) { setStatus(`Belum ada IFC untuk ${labels[building] || building}.`); return; }
  for (const d of entries) if (!loaded[d]) await loadDiscipline(d);
  Object.values(loaded).forEach(e => { e.model.visible = true; rebuildVisibleSubset(e, e.allIds).visible = true; e.model.visible = false; });
  const visible = visibleMesh(loaded[activeDiscipline]) || Object.values(loaded)[0]?.model;
  if (visible) frameObject(visible);
  setStatus(`Semua elemen yang pernah di-hide sudah ditampilkan lagi.`);
}

function setMouseFromEvent(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
}

function pick(event) {
  setMouseFromEvent(event);
  raycaster.setFromCamera(mouse, camera);
  const candidates = Object.values(loaded).map(e => visibleMesh(e)).filter(Boolean).filter(m => m.visible);
  const hit = raycaster.intersectObjects(candidates, false)[0];
  if (!hit) return null;
  const entry = Object.values(loaded).find(e => hit.object === visibleMesh(e));
  if (!entry) return null;
  const expressID = loader.ifcManager.getExpressId(hit.object.geometry, hit.faceIndex);
  return { entry, expressID, hit };
}

async function selectElement(event) {
  const result = pick(event);
  if (!result) { clearSelection(); setStatus('Tidak ada elemen terpilih.'); return null; }
  clearSelection();
  selected = result;
  loader.ifcManager.createSubset({
    modelID: result.entry.model.modelID,
    ids: [result.expressID],
    material: highlightMaterial,
    scene,
    removePrevious: true,
    customID: selectSubsetId(result.entry.discipline)
  }).renderOrder = 10;
  const label = await elementLabel(result.entry, result.expressID);
  setStatus(`Selected: ${label}. Klik kanan untuk Hide/Isolate.`);
  return result;
}

function showContextMenu(event) {
  contextMenu.style.left = `${event.clientX}px`;
  contextMenu.style.top = `${event.clientY}px`;
  contextMenu.style.display = 'block';
}
function hideContextMenu() { contextMenu.style.display = 'none'; }

function hideSelected() {
  if (!selected) return;
  const { entry, expressID } = selected;
  entry.visibleIds.delete(expressID);
  clearSelection();
  const subset = rebuildVisibleSubset(entry);
  subset.visible = true;
  setStatus(`Elemen #${expressID} disembunyikan. Pakai Show All Hidden untuk mengembalikan.`);
}
function isolateSelected() {
  if (!selected) return;
  const { entry, expressID } = selected;
  clearSelection();
  const subset = rebuildVisibleSubset(entry, [expressID]);
  subset.visible = true;
  setStatus(`Isolate elemen #${expressID}. Pakai Show All Hidden untuk kembali.`);
}

renderer.domElement.addEventListener('click', event => { hideContextMenu(); selectElement(event); });
renderer.domElement.addEventListener('contextmenu', async event => {
  event.preventDefault();
  await selectElement(event);
  showContextMenu(event);
});
document.addEventListener('click', event => { if (!contextMenu.contains(event.target) && event.target !== renderer.domElement) hideContextMenu(); });
contextMenu.addEventListener('click', event => {
  const action = event.target?.dataset?.menuAction;
  if (action === 'hide') hideSelected();
  if (action === 'isolate') isolateSelected();
  if (action === 'show-all') showAll();
  hideContextMenu();
});

document.querySelectorAll('[data-discipline]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-discipline]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    loadDiscipline(btn.dataset.discipline);
  });
});
document.getElementById('showAll').addEventListener('click', showAll);
document.getElementById('showHidden').addEventListener('click', showAll);
document.getElementById('sectionToggle').addEventListener('click', e => {
  sectionOn = !sectionOn;
  e.currentTarget.classList.toggle('active', sectionOn);
  Object.values(loaded).forEach(entry => {
    applyClipping(entry.model);
    const subset = visibleMesh(entry);
    if (subset) applyClipping(subset);
  });
  setStatus(sectionOn ? 'Section cut aktif. Prototype ini memakai potongan vertikal sederhana.' : 'Section cut nonaktif.');
});
document.getElementById('resetView').addEventListener('click', () => {
  const entry = loaded[activeDiscipline] || Object.values(loaded)[0];
  const visible = entry ? visibleMesh(entry) || entry.model : null;
  if (visible) frameObject(visible);
});
addEventListener('resize', () => {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
});
function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }
animate();
loadDiscipline(disciplineParam);
