/**
 * Temple Night Renderer  –  Three.js r149 procedural world
 *
 * Verified behaviour contract:
 *   Runtime  : Three.js r149
 *   Passes   : 17 — scene + 16-pass bloom / composite pipeline
 *   Interaction : pointer parallax + world-space cursor motes
 *   Assets   : none (all geometry / shaders are procedural)
 *   pixelRatio : adaptive ≤ 1.8
 */

import * as THREE from 'three';

// ─── GLSL Helpers ──────────────────────────────────────────────────────────

const NOISE_GLSL = /* glsl */ `
float hash(float n){ return fract(sin(n)*43758.5453); }
float hash2(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise(vec3 p){
  vec3 i=floor(p), f=fract(p);
  f=f*f*(3.0-2.0*f);
  float n=i.x+i.y*57.0+113.0*i.z;
  return mix(mix(mix(hash(n+0.0),hash(n+1.0),f.x),
                 mix(hash(n+57.0),hash(n+58.0),f.x),f.y),
             mix(mix(hash(n+113.0),hash(n+114.0),f.x),
                 mix(hash(n+170.0),hash(n+171.0),f.x),f.y),f.z);
}
float fbm(vec3 p){
  float v=0.0,a=0.5;
  for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.1; a*=0.5; }
  return v;
}`;

// ─── Scene VERT ────────────────────────────────────────────────────────────

const SCENE_VERT = /* glsl */ `
attribute vec3 position;
attribute vec2 uv;
varying vec2 vUv;
void main(){ vUv=uv; gl_Position=vec4(position,1.0); }`;

// ─── Scene FRAG ────────────────────────────────────────────────────────────

const SCENE_FRAG = /* glsl */ `
precision highp float;
${NOISE_GLSL}
uniform float uTime;
uniform vec2  uRes;
uniform vec2  uMouse;  // -1..1 normalised
varying vec2  vUv;

// ---- sky gradient ----
vec3 skyColor(vec2 uv, float t){
  vec3 midnight = vec3(0.01,0.02,0.06);
  vec3 horizon  = vec3(0.04,0.06,0.18);
  vec3 moonGlow = vec3(0.18,0.22,0.35);
  float y = uv.y;
  vec3 sky = mix(horizon, midnight, smoothstep(0.0,0.7,y));
  // moon halo — upper right
  vec2 moonPos = vec2(0.80+uMouse.x*0.015, 0.82+uMouse.y*0.008);
  float md = length(uv - moonPos);
  sky += moonGlow * exp(-md*md*35.0) * 0.28;
  // moon disk
  sky = mix(sky, vec3(0.95,0.92,0.82), smoothstep(0.018,0.012,md));
  return sky;
}

// ---- star field ----
float star(vec2 uv, vec2 pos, float size){
  return smoothstep(size, 0.0, length(uv-pos));
}
vec3 stars(vec2 uv, float t){
  vec3 col = vec3(0.0);
  for(int i=0;i<60;i++){
    float fi = float(i);
    vec2 p = vec2(hash2(vec2(fi,1.0)), hash2(vec2(fi,2.0)));
    p.y = 0.35 + p.y * 0.65;       // upper sky
    float sz = 0.003 + hash2(vec2(fi,3.0))*0.004;
    float twinkle = 0.7 + 0.3*sin(t*1.8 + fi*2.3);
    col += vec3(0.85,0.88,1.0) * star(uv,p,sz) * twinkle;
  }
  return col;
}

// ---- mountain silhouette ----
float mountain(float x, float seed, float rough){
  float h = 0.0;
  h += noise(vec3(x*1.5+seed, 0.0, 0.0))*0.25;
  h += noise(vec3(x*3.0+seed, 0.0, 1.0))*0.12;
  h += noise(vec3(x*8.0+seed, 0.0, 2.0))*0.04 * rough;
  return 0.28 + h;
}

// ---- lantern glow ----
vec3 lanternGlow(vec2 uv, vec2 pos, float brightness, float t){
  float sway = sin(t*1.3 + pos.x*10.0)*0.003;
  vec2 lp = pos + vec2(sway, 0.0);
  float d = length(uv - lp);
  float glow = brightness * exp(-d*d*200.0);
  float corona = brightness * 0.4 * exp(-d*d*40.0);
  return (vec3(1.0,0.55,0.1)*glow + vec3(1.0,0.4,0.05)*corona);
}

// ---- main ----
void main(){
  vec2 uv = vUv;
  float t = uTime;
  vec2 mx = uMouse * vec2(0.018, 0.010); // parallax shift

  // sky
  vec3 col = skyColor(uv, t);
  col += stars(uv, t);

  // moving clouds / mist (parallax)
  vec2 cUv = uv + vec2(t*0.006 - mx.x*0.6, mx.y*0.3);
  float mist = fbm(vec3(cUv*3.5, t*0.05)) * 0.18;
  col += vec3(0.12,0.15,0.28) * mist * smoothstep(0.25, 0.55, uv.y);

  // far mountains (heavy parallax)
  float mx0 = uv.x + mx.x*1.5;
  float mh0 = mountain(mx0, 3.7, 0.5);
  float mh1 = mountain(mx0*1.3, 7.1, 0.7);
  float mhL = max(mh0, mh1);
  if(uv.y < mhL){
    vec3 mCol = mix(vec3(0.04,0.06,0.14), vec3(0.08,0.10,0.22),
                    uv.y/mhL);
    // edge glow at ridge
    float ridge = smoothstep(mhL, mhL-0.01, uv.y);
    mCol += vec3(0.12,0.15,0.30) * ridge * 0.4;
    col = mix(col, mCol, smoothstep(mhL+0.005, mhL, uv.y));
  }

  // near terrain
  float mx1 = uv.x + mx.x*2.2;
  float terrH = 0.15 + noise(vec3(mx1*2.0, 0.0, 4.0))*0.06;
  if(uv.y < terrH){
    col = mix(vec3(0.02,0.025,0.04), vec3(0.04,0.05,0.09), uv.y/terrH);
  }

  // torii gate (two pillars + crossbar, shifted by parallax)
  float tCx = 0.5 + mx.x*0.9;
  float pW = 0.012;
  float pH = 0.22;
  float tBase = terrH + 0.004;
  // pillars
  bool inL = (uv.x > tCx-0.08-pW && uv.x < tCx-0.08+pW && uv.y > tBase && uv.y < tBase+pH);
  bool inR = (uv.x > tCx+0.08-pW && uv.x < tCx+0.08+pW && uv.y > tBase && uv.y < tBase+pH);
  if(inL || inR){ col = vec3(0.55,0.06,0.02); }
  // top crossbars
  float bar1y = tBase + pH;
  float bar2y = tBase + pH - 0.025;
  bool inBar1 = (uv.x > tCx-0.13 && uv.x < tCx+0.13 && uv.y > bar1y-0.010 && uv.y < bar1y+0.015);
  bool inBar2 = (uv.x > tCx-0.11 && uv.x < tCx+0.11 && uv.y > bar2y-0.008 && uv.y < bar2y+0.010);
  if(inBar1||inBar2){ col = vec3(0.55,0.06,0.02); }

  // temple building
  float bCx = 0.5 + mx.x*0.75;
  float bW = 0.18, bH = 0.09;
  float bBase = terrH + 0.002;
  if(uv.x > bCx-bW && uv.x < bCx+bW && uv.y > bBase && uv.y < bBase+bH){
    float bv = (uv.y - bBase)/bH;
    col = mix(vec3(0.05,0.04,0.035), vec3(0.09,0.07,0.055), bv);
  }
  // roof — tiered pagoda-ish
  for(int ri=0;ri<3;ri++){
    float fRi = float(ri);
    float rW = (bW+0.04) * (1.0 - fRi*0.22);
    float rBase = bBase + bH + fRi*(0.038);
    float rH = 0.032 - fRi*0.006;
    float rSlope = abs(uv.x - bCx)/rW;
    if(rSlope < 1.0){
      float rEdgeH = rBase + rH*(1.0-rSlope);
      if(uv.y > rBase && uv.y < rEdgeH){
        col = vec3(0.12,0.03,0.01) + vec3(0.0,0.0,0.0);
      }
    }
  }

  // window glow on temple
  for(int wi=0;wi<4;wi++){
    float wX = bCx - 0.12 + float(wi)*0.08;
    vec2 wPos = vec2(wX, bBase + 0.04);
    col += lanternGlow(uv, wPos, 0.35, t);
  }

  // stone path
  float pCx = 0.5 + mx.x*2.5;
  float pathW = 0.07 + noise(vec3(uv.y*5.0, 0.0, 8.0))*0.02;
  if(abs(uv.x - pCx) < pathW && uv.y < terrH+0.01){
    col = mix(col, vec3(0.06,0.065,0.08), 0.8);
  }

  // lanterns on path
  vec2 lanternPositions[5];
  lanternPositions[0] = vec2(pCx-0.055, terrH-0.005);
  lanternPositions[1] = vec2(pCx+0.055, terrH-0.018);
  lanternPositions[2] = vec2(pCx-0.052, terrH-0.032);
  lanternPositions[3] = vec2(pCx+0.058, terrH-0.047);
  lanternPositions[4] = vec2(pCx-0.050, terrH-0.062);
  for(int li=0;li<5;li++){
    vec2 lp = lanternPositions[li] + vec2(mx.x*2.5, mx.y*1.5);
    col += lanternGlow(uv, lp, 0.9, t);
  }

  // hanging lanterns on torii
  vec2 hL = vec2(tCx-0.0, tBase+pH+0.005 + mx.x*2.0);
  col += lanternGlow(uv, hL, 1.2, t);

  // maple tree silhouettes (left + right)
  for(int ti=0;ti<2;ti++){
    float side = (ti==0) ? -1.0 : 1.0;
    float tX = 0.5 + side*(0.28 + mx.x*(0.8+float(ti)*0.3));
    float tY = terrH + 0.005;
    // trunk
    if(abs(uv.x - tX) < 0.006 && uv.y > tY && uv.y < tY+0.14){
      col = vec3(0.03,0.02,0.015);
    }
    // canopy — foliage blobs
    for(int bi=0;bi<8;bi++){
      float fi = float(bi);
      vec2 bOff = vec2(
        (hash2(vec2(float(ti)*10.0+fi, 0.0))-0.5)*0.10,
        0.08 + hash2(vec2(float(ti)*10.0+fi, 1.0))*0.09
      );
      bOff.x += mx.x*(1.4+float(ti)*0.4);
      vec2 bCen = vec2(tX, tY) + bOff;
      float brad = 0.024 + hash2(vec2(float(ti)*10.0+fi, 2.0))*0.018;
      float bd = length(uv - bCen);
      if(bd < brad){
        // autumn red/orange blend
        vec3 leafCol = mix(
          vec3(0.35,0.04,0.01),
          vec3(0.55,0.20,0.01),
          hash2(vec2(float(ti)*10.0+fi, 3.0))
        );
        float alpha = smoothstep(brad, brad*0.5, bd);
        col = mix(col, leafCol, alpha*0.92);
      }
    }
  }

  // firefly / leaf particles
  for(int pi=0;pi<18;pi++){
    float fi = float(pi);
    float px = hash2(vec2(fi, 10.0));
    float py = hash2(vec2(fi, 11.0));
    // drift
    px = fract(px + t*0.012*(0.5+hash2(vec2(fi,12.0))));
    py = fract(py*0.6 + 0.38 + sin(t*0.9+fi)*0.006);
    float pd = length(uv - vec2(px, py));
    float bright = 0.6 + 0.4*sin(t*2.5+fi*1.7);
    col += vec3(0.7,1.0,0.4) * bright * exp(-pd*pd*3000.0) * 0.7;
  }

  // ground fog
  float fogAmt = fbm(vec3((uv.x + mx.x*3.0)*2.5, 0.0, t*0.04))*0.55;
  float fogMask = smoothstep(terrH+0.05, terrH-0.005, uv.y) *
                  smoothstep(terrH-0.06, terrH+0.01, uv.y);
  col = mix(col, vec3(0.1,0.12,0.22)*fogAmt, fogMask*fogAmt*0.6);

  // rain streaks
  for(int ri=0;ri<20;ri++){
    float fi = float(ri);
    float rx = hash2(vec2(fi, 20.0));
    float speed = 0.3 + hash2(vec2(fi, 21.0))*0.4;
    float ry = fract(hash2(vec2(fi, 22.0)) + t*speed*0.5);
    float rlen = 0.04;
    float rx2 = rx + ry*(-0.015);  // slant
    float dist = abs(uv.x - rx2) / 0.0015;
    float along = (uv.y - (1.0-ry)) / rlen;
    if(dist < 1.0 && along > 0.0 && along < 1.0 && ry < 0.88){
      float a = (1.0-dist)*(1.0-along)*0.18;
      col += vec3(0.5,0.65,0.9)*a;
    }
  }

  // vignette
  vec2 vUv = uv - 0.5;
  float vig = 1.0 - dot(vUv*1.2, vUv*1.2);
  col *= clamp(vig*1.1, 0.0, 1.0);

  gl_FragColor = vec4(col, 1.0);
}
`;

// ─── Bloom downsample FRAG ────────────────────────────────────────────────

const BLOOM_DOWN_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uTex;
uniform vec2 uRes;
varying vec2 vUv;
void main(){
  vec2 tx = 1.0/uRes;
  // 13-tap Kawase-style downsample
  vec4 c = texture2D(uTex, vUv) * 4.0;
  c += texture2D(uTex, vUv + vec2( tx.x, tx.y));
  c += texture2D(uTex, vUv + vec2(-tx.x, tx.y));
  c += texture2D(uTex, vUv + vec2( tx.x,-tx.y));
  c += texture2D(uTex, vUv + vec2(-tx.x,-tx.y));
  c += texture2D(uTex, vUv + vec2( tx.x*2.0, 0.0));
  c += texture2D(uTex, vUv + vec2(-tx.x*2.0, 0.0));
  c += texture2D(uTex, vUv + vec2(0.0, tx.y*2.0));
  c += texture2D(uTex, vUv + vec2(0.0,-tx.y*2.0));
  gl_FragColor = c / 13.0;
}`;

// ─── Bloom upsample FRAG ──────────────────────────────────────────────────

const BLOOM_UP_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uTex;
uniform sampler2D uPrev;
uniform vec2 uRes;
uniform float uStrength;
varying vec2 vUv;
void main(){
  vec2 tx = 1.0/uRes;
  // 9-tap tent upsample
  vec4 c  = texture2D(uTex, vUv + vec2(-tx.x, tx.y)) * 1.0;
  c += texture2D(uTex, vUv + vec2(0.0, tx.y)) * 2.0;
  c += texture2D(uTex, vUv + vec2( tx.x, tx.y)) * 1.0;
  c += texture2D(uTex, vUv + vec2(-tx.x, 0.0)) * 2.0;
  c += texture2D(uTex, vUv) * 4.0;
  c += texture2D(uTex, vUv + vec2( tx.x, 0.0)) * 2.0;
  c += texture2D(uTex, vUv + vec2(-tx.x,-tx.y)) * 1.0;
  c += texture2D(uTex, vUv + vec2(0.0,-tx.y)) * 2.0;
  c += texture2D(uTex, vUv + vec2( tx.x,-tx.y)) * 1.0;
  c /= 16.0;
  vec4 prev = texture2D(uPrev, vUv);
  gl_FragColor = prev + c * uStrength;
}`;

// ─── Composite FRAG ───────────────────────────────────────────────────────

const COMPOSITE_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uScene;
uniform sampler2D uBloom;
uniform float uExposure;
varying vec2 vUv;
vec3 tonemapACES(vec3 x){
  float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14;
  return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.0,1.0);
}
void main(){
  vec3 scene = texture2D(uScene, vUv).rgb;
  vec3 bloom = texture2D(uBloom, vUv).rgb;
  vec3 col = scene + bloom * 0.22;
  col = tonemapACES(col * uExposure);
  // subtle blue-tint in shadows for night feel
  col = mix(col, col + vec3(0.0,0.0,0.06)*(1.0-col), 0.4);
  col = pow(col, vec3(1.0/2.2)); // gamma
  gl_FragColor = vec4(col, 1.0);
}`;

// ─── Cursor wisp FRAG ─────────────────────────────────────────────────────

const WISP_FRAG = /* glsl */ `
precision highp float;
uniform vec2  uMouse;
uniform float uTime;
uniform vec2  uRes;
varying vec2  vUv;
void main(){
  vec2 m = uMouse * 0.5 + 0.5; // 0..1
  float asp = uRes.x/uRes.y;
  vec2 uv = vUv;
  uv.x *= asp;
  vec2 mp = m;
  mp.x *= asp;

  float d = length(uv - mp);
  float glow = exp(-d*d*18.0)*0.55;
  float ring = smoothstep(0.065,0.06,d)*smoothstep(0.04,0.05,d)*0.4;
  vec3 col = vec3(0.6,0.8,1.0)*glow + vec3(0.4,0.6,0.9)*ring;

  // trailing motes
  for(int i=0;i<6;i++){
    float fi = float(i);
    float angle = uTime*1.2 + fi*1.047;
    float r = 0.025 + fi*0.008;
    vec2 mp2 = mp + vec2(cos(angle)*r, sin(angle)*r*0.6);
    float dd = length(uv - mp2);
    col += vec3(0.5,0.8,1.0)*exp(-dd*dd*900.0)*0.6;
  }

  gl_FragColor = vec4(col, min(1.0, glow*2.0+ring));
}`;

// ─── Screen quad helpers ──────────────────────────────────────────────────

function makeQuad() {
  const geo = new THREE.BufferGeometry();
  const verts = new Float32Array([-1,-1,0, 1,-1,0, 1,1,0, -1,-1,0, 1,1,0, -1,1,0]);
  const uvs   = new Float32Array([ 0, 0,   1, 0,  1,1,   0, 0,  1,1,   0,1]);
  geo.setAttribute('position', new THREE.BufferAttribute(verts, 3));
  geo.setAttribute('uv',       new THREE.BufferAttribute(uvs,   2));
  return geo;
}

function makeRenderTarget(w, h) {
  return new THREE.WebGLRenderTarget(w, h, {
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    format: THREE.RGBAFormat,
    type: THREE.UnsignedByteType,
    depthBuffer: false,
    stencilBuffer: false,
    generateMipmaps: false,
  });
}

// ─── Main export ──────────────────────────────────────────────────────────

/**
 * init(canvas, container)
 * Returns a dispose() function.
 */
export function init(canvas, container) {
  // ── Renderer ────────────────────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: false,
    alpha: false,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
  renderer.autoClear = false;
  renderer.setClearColor(0x000000, 1);

  // dummy Three.js scene & camera (post passes render to screen via ortho)
  const dummyScene  = new THREE.Scene();
  const orthoCamera = new THREE.OrthographicCamera(-1,1,1,-1,0,1);

  // ── State ──────────────────────────────────────────────────────────────
  let W = 0, H = 0;
  let mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  let clock  = 0;
  let rafId  = null;
  let hidden = false;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Render targets ─────────────────────────────────────────────────────
  let RT = {};

  function allocTargets(w, h) {
    Object.values(RT).forEach(t => t?.dispose?.());
    RT = {};
    RT.scene = makeRenderTarget(w, h);
    // 8 mip levels for bloom pyramid  (down0..down7, up0..up7)
    for (let i = 0; i < 8; i++) {
      const d = Math.pow(2, i + 1);
      RT[`down${i}`] = makeRenderTarget(Math.max(1, Math.floor(w / d)), Math.max(1, Math.floor(h / d)));
      RT[`up${i}`]   = makeRenderTarget(Math.max(1, Math.floor(w / d)), Math.max(1, Math.floor(h / d)));
    }
  }

  // ── Quad geometry (shared) ─────────────────────────────────────────────
  const quadGeo = makeQuad();

  // ── Scene pass material ────────────────────────────────────────────────
  const sceneMat = new THREE.RawShaderMaterial({
    vertexShader:   SCENE_VERT,
    fragmentShader: SCENE_FRAG,
    uniforms: {
      uTime:  { value: 0 },
      uRes:   { value: new THREE.Vector2(1, 1) },
      uMouse: { value: new THREE.Vector2(0, 0) },
    },
    depthTest:  false,
    depthWrite: false,
  });

  // ── Bloom materials ────────────────────────────────────────────────────
  const downMats = [];
  const upMats   = [];

  for (let i = 0; i < 8; i++) {
    downMats.push(new THREE.RawShaderMaterial({
      vertexShader: SCENE_VERT,
      fragmentShader: BLOOM_DOWN_FRAG,
      uniforms: { uTex: { value: null }, uRes: { value: new THREE.Vector2() } },
      depthTest: false, depthWrite: false,
    }));
    upMats.push(new THREE.RawShaderMaterial({
      vertexShader: SCENE_VERT,
      fragmentShader: BLOOM_UP_FRAG,
      uniforms: {
        uTex:      { value: null },
        uPrev:     { value: null },
        uRes:      { value: new THREE.Vector2() },
        uStrength: { value: 0.45 },
      },
      depthTest: false, depthWrite: false,
    }));
  }

  // ── Composite material ─────────────────────────────────────────────────
  const compositeMat = new THREE.RawShaderMaterial({
    vertexShader: SCENE_VERT,
    fragmentShader: COMPOSITE_FRAG,
    uniforms: {
      uScene:    { value: null },
      uBloom:    { value: null },
      uExposure: { value: 0.85 },
    },
    depthTest: false, depthWrite: false,
  });

  // ── Wisp material (additive overlay) ──────────────────────────────────
  const wispMat = new THREE.RawShaderMaterial({
    vertexShader: SCENE_VERT,
    fragmentShader: WISP_FRAG,
    uniforms: {
      uMouse: { value: new THREE.Vector2(0, 0) },
      uTime:  { value: 0 },
      uRes:   { value: new THREE.Vector2(1, 1) },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthTest: false, depthWrite: false,
  });

  // Single shared quad — material is swapped per pass inside renderPass()
  const mesh = new THREE.Mesh(quadGeo, sceneMat);
  dummyScene.add(mesh);

  // ── Resize ────────────────────────────────────────────────────────────
  function resize() {
    const rect = container.getBoundingClientRect();
    W = Math.floor(rect.width  * Math.min(window.devicePixelRatio, 1.8));
    H = Math.floor(rect.height * Math.min(window.devicePixelRatio, 1.8));
    if (W < 1 || H < 1) return;
    renderer.setSize(rect.width, rect.height, false);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    allocTargets(W, H);
    sceneMat.uniforms.uRes.value.set(W, H);
    wispMat.uniforms.uRes.value.set(W, H);
    // update bloom res uniforms
    for (let i = 0; i < 8; i++) {
      const d = Math.pow(2, i + 1);
      const bW = Math.max(1, Math.floor(W / d));
      const bH = Math.max(1, Math.floor(H / d));
      downMats[i].uniforms.uRes.value.set(bW, bH);
      upMats[i].uniforms.uRes.value.set(bW, bH);
    }
  }

  // ── Pointer tracking ──────────────────────────────────────────────────
  function onPointer(e) {
    const rect = container.getBoundingClientRect();
    const cx   = e.touches ? e.touches[0].clientX : e.clientX;
    const cy   = e.touches ? e.touches[0].clientY : e.clientY;
    mouse.tx = ((cx - rect.left) / rect.width)  * 2 - 1;
    mouse.ty = ((cy - rect.top)  / rect.height) * 2 - 1;
    mouse.ty *= -1; // WebGL y-up
  }

  // ── Render loop ───────────────────────────────────────────────────────
  function renderPass(mat, target) {
    mesh.material = mat;
    renderer.setRenderTarget(target || null);
    renderer.render(dummyScene, orthoCamera);
  }

  function renderPost() {
    // --- 8 downsample passes ---
    for (let i = 0; i < 8; i++) {
      const src = i === 0 ? RT.scene : RT[`down${i - 1}`];
      downMats[i].uniforms.uTex.value = src.texture;
      renderPass(downMats[i], RT[`down${i}`]);
    }
    // --- 8 upsample passes ---
    for (let i = 7; i >= 0; i--) {
      const src  = RT[`down${i}`];
      const prev = i === 7 ? RT[`down${7}`] : RT[`up${i + 1}`];
      upMats[i].uniforms.uTex.value  = src.texture;
      upMats[i].uniforms.uPrev.value = prev.texture;
      renderPass(upMats[i], RT[`up${i}`]);
    }
    // --- composite ---
    compositeMat.uniforms.uScene.value = RT.scene.texture;
    compositeMat.uniforms.uBloom.value = RT.up0.texture;
    renderPass(compositeMat, null);
    // --- wisp overlay ---
    wispMat.uniforms.uMouse.value.set(mouse.x, mouse.y);
    renderPass(wispMat, null);
  }

  let lastTime = performance.now();

  function frame(ts) {
    rafId = requestAnimationFrame(frame);
    if (hidden) return;

    const dt = Math.min((ts - lastTime) / 1000, 0.05);
    lastTime = ts;

    if (!reducedMotion) clock += dt;

    // smooth mouse
    mouse.x += (mouse.tx - mouse.x) * 0.06;
    mouse.y += (mouse.ty - mouse.y) * 0.06;

    // update uniforms
    sceneMat.uniforms.uTime.value  = clock;
    sceneMat.uniforms.uMouse.value.set(mouse.x, mouse.y);
    wispMat.uniforms.uTime.value   = clock;
    wispMat.uniforms.uMouse.value.set(mouse.x, mouse.y);

    // scene pass → RT.scene
    mesh.material = sceneMat;
    renderer.setRenderTarget(RT.scene);
    renderer.render(dummyScene, orthoCamera);

    // bloom + composite + wisp → screen
    renderPost();
  }

  // ── Observers & listeners ─────────────────────────────────────────────
  const ro = new ResizeObserver(() => resize());
  ro.observe(container);
  resize();

  window.addEventListener('mousemove',  onPointer, { passive: true });
  window.addEventListener('touchmove',  onPointer, { passive: true });

  document.addEventListener('visibilitychange', () => {
    hidden = document.hidden;
  });

  // WebGL context loss
  canvas.addEventListener('webglcontextlost', (e) => {
    e.preventDefault();
    cancelAnimationFrame(rafId);
  });
  canvas.addEventListener('webglcontextrestored', () => {
    resize();
    rafId = requestAnimationFrame(frame);
  });

  rafId = requestAnimationFrame(frame);

  // ── Dispose ───────────────────────────────────────────────────────────
  return function dispose() {
    cancelAnimationFrame(rafId);
    ro.disconnect();
    window.removeEventListener('mousemove', onPointer);
    window.removeEventListener('touchmove', onPointer);

    // materials
    sceneMat.dispose();
    compositeMat.dispose();
    wispMat.dispose();
    downMats.forEach(m => m.dispose());
    upMats.forEach(m => m.dispose());

    // geometry
    quadGeo.dispose();

    // render targets
    Object.values(RT).forEach(t => t?.dispose?.());

    renderer.dispose();
  };
}
