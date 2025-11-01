import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.161/build/three.module.js";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.161/examples/jsm/controls/OrbitControls.js";
import { RGBELoader } from "https://cdn.jsdelivr.net/npm/three@0.161/examples/jsm/loaders/RGBELoader.js";

console.log("container size:", W, H);
console.log("leaves:", leaves);



const el = document.getElementById('app');
const W = el.clientWidth, H = el.clientHeight;

// ---- data ----
const data = {name:"closet", children:[
  {name:"COS · XS", value:12, hue:260},
  {name:"Sies Marjan · 0/XS", value:11, hue:300},
  {name:"Róhe · EU32", value:8, hue:230},
  {name:"AYR · 26S", value:6, hue:210},
  {name:"Zara · M", value:5, hue:235},
  {name:"Alexis · S", value:7, hue:48},
  {name:"Georgia Hardinge · UK8", value:9, hue:12}
]};

// ---- d3 layout ----
const pad=10;
const root=d3.treemap().size([W,H]).padding(pad).round(true)(
  d3.hierarchy(data).sum(d=>d.value)
);
const leaves=root.leaves();

// ---- three scene ----
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(35,W/H,0.1,100);
camera.position.set(0,0,12);

const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(2,window.devicePixelRatio));
renderer.setSize(W,H);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
el.appendChild(renderer.domElement);

// slight tilt for parallax
scene.rotation.x=-0.12; scene.rotation.y=0.08;

// lights
const key=new THREE.DirectionalLight(0xffffff,1.3);
key.position.set(2,3,4); scene.add(key);
const hemi=new THREE.HemisphereLight(0xffffff,0x223344,.6);
scene.add(hemi);

// mouse-driven highlight
window.addEventListener('pointermove',e=>{
  const x=(e.clientX/window.innerWidth)*2-1;
  const y=(e.clientY/window.innerHeight)*2-1;
  key.position.set(4*x,2.5-3*y,5).normalize().multiplyScalar(6);
});

// controls (disabled UI, but keep camera handy)
const controls=new OrbitControls(camera,renderer.domElement);
controls.enablePan=false; controls.enableZoom=false; controls.enableRotate=false;

// ---- build immediately (env map comes later) ----
buildTreemap();

// then load HDRI to add reflections
const pmrem=new THREE.PMREMGenerator(renderer);
new RGBELoader()
  .setDataType(THREE.FloatType)
  .load("https://cdn.jsdelivr.net/gh/pmndrs/drei-assets@master/hdri/venice_sunset_1k.hdr",(hdr)=>{
    const env=pmrem.fromEquirectangular(hdr).texture;
    scene.environment=env;
    scene.traverse(o=>{
      if(o.material && o.material.envMapIntensity!==undefined){
        o.material.envMapIntensity=1.25;
        o.material.needsUpdate=true;
      }
    });
  });

// ---- helpers ----

// handmade rounded-rect geometry (no external import needed)
function roundedRectGeometry(w, h, r, segments=8){
  const shape = new THREE.Shape();
  const x = -w/2, y = -h/2;
  const rr = Math.min(r, Math.min(w,h)/2);

  shape.moveTo(x+rr, y);
  shape.lineTo(x+w-rr, y);
  shape.quadraticCurveTo(x+w, y, x+w, y+rr);
  shape.lineTo(x+w, y+h-rr);
  shape.quadraticCurveTo(x+w, y+h, x+w-rr, y+h);
  shape.lineTo(x+rr, y+h);
  shape.quadraticCurveTo(x, y+h, x, y+h-rr);
  shape.lineTo(x, y+rr);
  shape.quadraticCurveTo(x, y, x+rr, y);

  return new THREE.ShapeGeometry(shape, segments);
}

// tiny noise normal for micro texture
function noiseTexture(){
  const size=64, data=new Uint8Array(size*size*4);
  for(let i=0;i<size*size;i++){
    const v=128+(Math.random()*50-25);
    data[i*4+0]=128; data[i*4+1]=v; data[i*4+2]=255; data[i*4+3]=255;
  }
  const tex=new THREE.DataTexture(data,size,size,THREE.RGBAFormat);
  tex.needsUpdate=true; tex.wrapS=tex.wrapT=THREE.RepeatWrapping; tex.repeat.set(8,8);
  return tex;
}

function buildTreemap(){
  const group=new THREE.Group(); scene.add(group);
  const radius=0.35;

  leaves.forEach(d=>{
    const x=d.x0-W/2, y=-(d.y0-H/2);
    const w=d.x1-d.x0, h=d.y1-d.y0;

    const geo=roundedRectGeometry(w/70, h/70, radius/70, 10);
    const hsl=new THREE.Color().setHSL((d.data.hue%360)/360,0.62,0.55);

    const mat=new THREE.MeshPhysicalMaterial({
      color:hsl, metalness:.25, roughness:.18,
      clearcoat:1, clearcoatRoughness:.06,
      sheen:1, sheenColor:new THREE.Color().setHSL((d.data.hue+40)/360,.9,.8),
      iridescence:.35, iridescenceIOR:1.3,
      envMapIntensity:.0 // bumped after HDRI loads
    });
    mat.normalMap=noiseTexture();
    mat.normalScale=new THREE.Vector2(.35,.35);

    const mesh=new THREE.Mesh(geo,mat);
    mesh.position.set((x+w/2)/70,(y-h/2)/70,0);
    mesh.rotation.z=(Math.random()-.5)*.02;
    mesh.rotation.x=(Math.random()-.5)*.02;
    group.add(mesh);

    const frame=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.10}));
    frame.scale.set(1.002,1.002,1); mesh.add(frame);

    const label=document.createElement('div');
    label.className='label'; label.textContent=d.data.name;
    label.style.left=`${d.x0+12}px`; label.style.top=`${d.y1-28}px`;
    el.appendChild(label);
  });
}

// animate
renderer.setAnimationLoop(()=>{ scene.rotation.z+=0.0006; renderer.render(scene,camera); });

// resize
window.addEventListener('resize',()=>{
  const w=el.clientWidth,h=el.clientHeight;
  renderer.setSize(w,h); camera.aspect=w/h; camera.updateProjectionMatrix();
});
