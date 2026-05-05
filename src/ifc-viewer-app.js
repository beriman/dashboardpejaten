import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { IFCLoader } from 'web-ifc-three/IFCLoader.js';

const params = new URLSearchParams(location.search);
const building = (params.get('building') || 'D').toUpperCase();
const disciplineParam = (params.get('discipline') || 'STR').toUpperCase();
const labels = { B: 'Gedung B', D: 'Gedung D', K: 'Gedung K' };
document.getElementById('buildingLabel').textContent = labels[building] || `Gedung ${building}`;

const modelMap = {
  D: { STR: '/models/Gedung D/IFC/STR/STR D.ifc' }
};

const status = document.getElementById('status');
const container = document.getElementById('viewer');
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
const loader = new IFCLoader();
loader.ifcManager.setWasmPath('/vendor/web-ifc/', true);

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
  const url = modelMap[building]?.[discipline];
  if (!url) {
    setStatus(`${labels[building] || building} - ${discipline} belum ada file IFC di paket dashboard. Upload/export IFC dulu lalu publish ulang.`);
    return;
  }
  if (loaded[discipline]) {
    Object.values(loaded).forEach(m => m.visible = false);
    loaded[discipline].visible = true;
    frameObject(loaded[discipline]);
    setStatus(`Menampilkan ${labels[building]} - ${discipline}.`);
    return;
  }
  setStatus(`Memuat ${discipline}: ${url}`);
  try {
    const model = await loader.loadAsync(url);
    model.name = `${building}-${discipline}`;
    model.traverse(child => {
      if (child.material) {
        child.material.clippingPlanes = sectionOn ? [clippingPlane] : [];
        child.material.clipShadows = true;
        child.material.side = THREE.DoubleSide;
      }
    });
    loaded[discipline] = model;
    Object.values(loaded).forEach(m => m.visible = false);
    model.visible = true;
    scene.add(model);
    frameObject(model);
    setStatus(`Berhasil memuat ${labels[building]} - ${discipline}. Gunakan mouse untuk orbit/pan/zoom.`);
  } catch (err) {
    console.error(err);
    setStatus(`Gagal memuat IFC ${discipline}. Detail: ${err?.message || err}`);
  }
}

async function showAll() {
  const entries = Object.keys(modelMap[building] || {});
  if (!entries.length) { setStatus(`Belum ada IFC untuk ${labels[building] || building}.`); return; }
  for (const d of entries) await loadDiscipline(d);
  Object.values(loaded).forEach(m => m.visible = true);
  const visible = Object.values(loaded)[0];
  if (visible) frameObject(visible);
  setStatus(`Menampilkan semua IFC tersedia untuk ${labels[building] || building}: ${entries.join(', ')}.`);
}

document.querySelectorAll('[data-discipline]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-discipline]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    loadDiscipline(btn.dataset.discipline);
  });
});
document.getElementById('showAll').addEventListener('click', showAll);
document.getElementById('sectionToggle').addEventListener('click', e => {
  sectionOn = !sectionOn;
  e.currentTarget.classList.toggle('active', sectionOn);
  Object.values(loaded).forEach(model => model.traverse(child => {
    if (child.material) child.material.clippingPlanes = sectionOn ? [clippingPlane] : [];
  }));
  setStatus(sectionOn ? 'Section cut aktif. Prototype ini memakai potongan vertikal sederhana.' : 'Section cut nonaktif.');
});
document.getElementById('resetView').addEventListener('click', () => {
  const visible = Object.values(loaded).find(m => m.visible) || Object.values(loaded)[0];
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
