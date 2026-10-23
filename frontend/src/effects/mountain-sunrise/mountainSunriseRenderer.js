/**
 * Mountain Sunrise Renderer  –  Three.js r149 procedural world
 *
 * Scene: alpenglow sunrise over layered mountain ranges
 *   – sky washes from deep indigo → violet → rose → amber → gold
 *   – sun crests the central peak with a corona bloom
 *   – 5 mountain layers with parallax depth
 *   – pine forest silhouettes on ridges
 *   – animated mist rivers in valleys
 *   – golden light-ray fans (volumetric crepuscular approximation)
 *   – drifting dawn birds (V-formations)
 *   – snow highlights on peak caps
 *   – pointer parallax + cursor wisps
 *   – 17 passes: scene + 8-down + 8-up bloom + ACES composite + wisp
 */

import * as THREE from 'three';

// ─── Shared GLSL noise ──────────────────────────────────────────────────────

const NOISE_GLSL = /* glsl */ `
float hash(float n){ return fract(sin(n)*43758.5453); }
float hash2f(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise3(vec3 p){
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
  for(int i=0;i<5;i++){ v+=a*noise3(p); p*=2.1; a*=0.5; }
  return v;
}`;

// ─── Vertex shader (shared) ──────────────────────────────────────────────────

const VERT = /* glsl */ `
attribute vec3 position;
attribute vec2 uv;
varying vec2 vUv;
void main(){ vUv=uv; gl_Position=vec4(position,1.0); }`;

// ─── Scene fragment ──────────────────────────────────────────────────────────

const SCENE_FRAG = /* glsl */ `
precision highp float;
${NOISE_GLSL}

uniform float uTime;
uniform vec2  uRes;
uniform vec2  uMouse;
varying vec2  vUv;

// ── Sky gradient: deep night-blue at top → rose alpenglow → gold at horizon ──
vec3 skyColor(vec2 uv, float t){
  // animate sunrise: over ~60 s cycle sun rises
  float cycle = mod(t * 0.012, 1.0);   // 0=pre-dawn, 0.3=golden hour, 0.7=full day

  // palette anchors
  vec3 zenith    = mix(vec3(0.04,0.04,0.18), vec3(0.28,0.52,0.88), smoothstep(0.0,0.5,cycle));
  vec3 midSky    = mix(vec3(0.14,0.06,0.22), vec3(0.55,0.78,0.98), smoothstep(0.0,0.6,cycle));
  vec3 rose      = mix(vec3(0.55,0.12,0.22), vec3(0.90,0.70,0.55), smoothstep(0.1,0.6,cycle));
  vec3 amber     = mix(vec3(0.70,0.22,0.05), vec3(0.98,0.85,0.50), smoothstep(0.1,0.55,cycle));
  vec3 horizon   = mix(vec3(0.80,0.30,0.10), vec3(1.0,0.95,0.75), smoothstep(0.2,0.6,cycle));

  float y = uv.y;
  vec3 sky;
  if(y > 0.6)      sky = mix(midSky,  zenith, (y-0.6)/0.4);
  else if(y > 0.4) sky = mix(rose,    midSky, (y-0.4)/0.2);
  else if(y > 0.2) sky = mix(amber,   rose,   (y-0.2)/0.2);
  else             sky = mix(horizon,  amber,  y/0.2);

  return sky;
}

// ── Sun position + corona ────────────────────────────────────────────────────
float sunY(float t){
  float cycle = mod(t*0.012, 1.0);
  // sun rises from below mountains (~0.35) to ~0.6
  return 0.28 + cycle * 0.38;
}

vec3 sunBloom(vec2 uv, float t, vec2 mx){
  float cycle = mod(t*0.012, 1.0);
  float sx = 0.50 + mx.x*0.012;
  float sy = sunY(t) + mx.y*0.008;
  float d  = length(uv - vec2(sx, sy));

  vec3 sunCol = mix(vec3(1.0,0.35,0.05), vec3(1.0,0.96,0.70), smoothstep(0.0,0.5,cycle));
  // corona layers
  float c1 = exp(-d*d*180.0) * 1.8;
  float c2 = exp(-d*d*30.0)  * 0.9;
  float c3 = exp(-d*d*6.0)   * 0.4;
  // disk
  float disk = smoothstep(0.022, 0.012, d);
  return sunCol*(c1+c2+c3) + vec3(1.0,0.98,0.85)*disk;
}

// ── Crepuscular light rays ───────────────────────────────────────────────────
float lightRays(vec2 uv, float t, vec2 mx){
  float sx = 0.50 + mx.x*0.012;
  float sy = sunY(t);
  float cycle = mod(t*0.012, 1.0);
  float intensity = smoothstep(0.0, 0.35, cycle) * (1.0 - smoothstep(0.6, 0.85, cycle));

  vec2 toSun = vec2(sx, sy) - uv;
  float angle = atan(toSun.x, toSun.y);
  float r = length(toSun);

  // 12 radial rays
  float rays = 0.0;
  for(int i=0;i<12;i++){
    float fi = float(i);
    float rayAngle = fi * 3.14159 / 6.0 + t*0.04;
    float da = abs(mod(angle - rayAngle + 3.14159, 6.28318) - 3.14159);
    rays += exp(-da*da*60.0) * exp(-r*r*3.0);
  }
  return rays * intensity * 0.25;
}

// ── Mountain ridge profile ───────────────────────────────────────────────────
float ridge(float x, float seed, float scale){
  float h=0.0;
  h += noise3(vec3(x*scale      + seed, 0.0, 0.0))*0.30;
  h += noise3(vec3(x*scale*2.0  + seed, 0.0, 1.0))*0.15;
  h += noise3(vec3(x*scale*5.0  + seed, 0.0, 2.0))*0.05;
  h += noise3(vec3(x*scale*12.0 + seed, 0.0, 3.0))*0.015;
  return h;
}

// ── Pine tree silhouette ─────────────────────────────────────────────────────
float pine(vec2 uv, vec2 base, float h){
  float dx = (uv.x - base.x);
  float dy = (uv.y - base.y);
  if(dy < 0.0 || dy > h) return 0.0;
  // triangular taper with multiple tiers
  float tier = mod(dy/h * 4.0, 1.0);
  float maxW = (1.0 - dy/h) * 0.012 * (1.0 - tier*0.4);
  return step(abs(dx), maxW) * step(0.0, dy) * step(dy, h);
}

// ── Mist ribbons ─────────────────────────────────────────────────────────────
float mist(vec2 uv, float t){
  // drifting horizontal layers
  float m = 0.0;
  for(int i=0;i<4;i++){
    float fi = float(i);
    float yBand = 0.22 + fi*0.04;
    float drift = t*0.008*(0.5+fi*0.3);
    float nx = fbm(vec3((uv.x + drift)*2.5, 0.0, fi*3.7+1.0));
    float ny = fbm(vec3((uv.x + drift)*2.5, 0.0, fi*3.7+2.0));
    float band = exp(-pow((uv.y - yBand + ny*0.02)*28.0, 2.0));
    m += band * (0.4 + nx*0.4);
  }
  return clamp(m, 0.0, 1.0);
}

// ── Dawn birds (V-formation) ─────────────────────────────────────────────────
float bird(vec2 uv, vec2 pos, float wing){
  // two curved wings
  float dx = uv.x - pos.x;
  float dy = uv.y - pos.y;
  float ldx = dx + wing*0.012;
  float rdx = dx - wing*0.012;
  float l = length(vec2(ldx, dy - abs(ldx)*1.8));
  float r = length(vec2(rdx, dy - abs(rdx)*1.8));
  return smoothstep(0.006, 0.001, min(l, r));
}

// ─────────────────────────────────────────────────────────────────────────────
void main(){
  vec2 uv = vUv;
  float t  = uTime;
  vec2 mx  = uMouse * vec2(0.016, 0.008);
  float cycle = mod(t*0.012, 1.0);

  // sky
  vec3 col = skyColor(uv, t);

  // sun bloom + corona
  col += sunBloom(uv, t, mx);

  // crepuscular rays
  col += vec3(1.0,0.82,0.50) * lightRays(uv, t, mx);

  // atmospheric haze near horizon (parallax)
  vec2 hUv = uv + vec2(-mx.x*0.5, mx.y*0.2);
  float haze = exp(-pow((hUv.y - 0.28)*10.0, 2.0)) * 0.55;
  vec3 hazeCol = mix(vec3(1.0,0.65,0.30), vec3(0.9,0.85,0.75), cycle);
  col = mix(col, hazeCol, haze * smoothstep(0.3,0.0,abs(uv.y-0.28)));

  // ── Mountain layers (back → front) ─────────────────────────────────
  // Each layer: deeper parallax, darker/bluer for distant, warmer for near

  // Layer 5 – farthest, blue-grey
  {
    float px = uv.x + mx.x * 0.3;
    float h = 0.52 + ridge(px, 11.3, 0.8) * 0.22;
    float rimLight = exp(-pow((uv.y-h)*60.0,2.0)) * smoothstep(0.4,0.0,cycle);
    if(uv.y < h){
      vec3 mc = mix(vec3(0.22,0.24,0.38), vec3(0.40,0.45,0.60), uv.y/h);
      col = mix(col, mc + vec3(0.8,0.6,0.4)*rimLight*0.3, smoothstep(h+0.008, h, uv.y));
    }
  }
  // Layer 4 – violet-slate
  {
    float px = uv.x + mx.x * 0.55;
    float h = 0.44 + ridge(px, 7.1, 1.1) * 0.20;
    float rimLight = exp(-pow((uv.y-h)*55.0,2.0));
    vec3 rimCol = mix(vec3(1.0,0.5,0.2), vec3(1.0,0.8,0.5), cycle);
    if(uv.y < h){
      vec3 mc = mix(vec3(0.14,0.13,0.25), vec3(0.28,0.26,0.42), uv.y/h);
      col = mix(col, mc + rimCol*rimLight*0.5, smoothstep(h+0.006, h, uv.y));
    }
  }
  // Layer 3 – main drama peaks (tallest, central peak catches sun)
  {
    float px = uv.x + mx.x * 0.80;
    float baseH = 0.34 + ridge(px, 3.7, 1.4) * 0.22;
    // central peak spike
    float cp = 1.0 - abs(uv.x - 0.50 - mx.x*0.8) / 0.18;
    float peakBoost = max(0.0, cp) * 0.12;
    float h = baseH + peakBoost;
    // snow cap on peak
    float snowLine = 0.56 + ridge(px, 99.0, 4.0)*0.03;
    float rimLight = exp(-pow((uv.y-h)*50.0,2.0));
    vec3 rimCol = mix(vec3(1.0,0.4,0.1)*1.6, vec3(1.0,0.90,0.65)*1.2, cycle);
    if(uv.y < h){
      vec3 mc = mix(vec3(0.07,0.06,0.12), vec3(0.18,0.16,0.26), uv.y/h);
      // sun warmth on lit slopes
      float lit = max(0.0, 0.5 - abs(px - 0.50)) * cycle * 2.0;
      mc += vec3(0.6,0.35,0.10) * lit;
      // snow
      mc = mix(mc, vec3(0.95,0.90,0.85)+rimCol*0.15, smoothstep(snowLine-0.02, snowLine, uv.y/h));
      col = mix(col, mc + rimCol*rimLight*0.7, smoothstep(h+0.005, h, uv.y));
    }
  }
  // Layer 2 – dark foreground range
  {
    float px = uv.x + mx.x * 1.3;
    float h = 0.26 + ridge(px, 5.5, 1.8) * 0.12;
    // pine trees on ridge
    float pines = 0.0;
    for(int pi=0;pi<18;pi++){
      float fi = float(pi);
      float pX = fract(fi*0.0613 + 0.03) - mx.x*1.3;
      float pBase = h - 0.003 + ridge(pX+px, 55.0+fi, 6.0)*0.008;
      pines += pine(uv, vec2(pX, pBase), 0.04 + fi*0.001);
    }
    if(uv.y < h || pines > 0.0){
      vec3 mc = vec3(0.06,0.055,0.045);
      // alpenglow pink tinge on ridgeline
      float rim = exp(-pow((uv.y-h)*40.0,2.0));
      mc += mix(vec3(0.5,0.15,0.05), vec3(0.9,0.6,0.3), cycle) * rim * 0.6;
      col = mix(col, mc, smoothstep(max(h,pines>0.0?uv.y:0.0)+0.004, max(h,0.0), uv.y));
      if(pines > 0.0) col = mix(col, mc, pines);
    }
  }
  // Layer 1 – closest, ground
  {
    float px = uv.x + mx.x * 2.0;
    float h = 0.12 + ridge(px, 2.2, 2.5)*0.04;
    if(uv.y < h){
      vec3 gc = mix(vec3(0.04,0.035,0.03), vec3(0.12,0.09,0.06), uv.y/h);
      // warm golden light on ground near sunrise
      gc += vec3(0.4,0.25,0.05) * cycle * (1.0 - uv.y/h);
      col = mix(col, gc, 1.0);
    }
    // foreground pine silhouettes
    for(int pi=0;pi<10;pi++){
      float fi = float(pi);
      float pX = fract(fi*0.097 + 0.05) - mx.x*2.0;
      float pBase = h + ridge(pX+px, 80.0+fi, 9.0)*0.01;
      float v = pine(uv, vec2(pX, pBase), 0.07 + hash2f(vec2(fi,0.0))*0.03);
      if(v > 0.0) col = mix(col, vec3(0.025,0.02,0.015), v);
    }
  }

  // ── Valley mist ──────────────────────────────────────────────────────
  float mistAmt = mist(uv + vec2(-mx.x*2.5, 0.0), t);
  float mistMask = smoothstep(0.32, 0.18, uv.y) * smoothstep(0.10, 0.20, uv.y);
  vec3 mistCol = mix(vec3(0.9,0.7,0.5), vec3(1.0,0.95,0.90), cycle);
  col = mix(col, mistCol, mistAmt * mistMask * 0.55);

  // ── Dawn birds ───────────────────────────────────────────────────────
  for(int bi=0;bi<3;bi++){
    float fi = float(bi);
    // V-formation drifts right
    float bx = fract(0.1 + fi*0.22 + t*0.018*(0.6+fi*0.2));
    float by = 0.55 + fi*0.025 + sin(t*0.3+fi*1.4)*0.008;
    bx = bx + mx.x*0.5;
    // 5 birds per formation
    for(int si=0;si<5;si++){
      float fs = float(si);
      float vx = bx + (fs-2.0)*0.018;
      float vy = by + abs(fs-2.0)*0.012;
      float wing = 0.6 + sin(t*3.5 + fi*1.7 + fs*0.9)*0.4;
      col += vec3(0.04,0.03,0.02) * bird(uv, vec2(vx,vy), wing);
    }
  }

  // ── Atmospheric glow overlay (horizon band) ───────────────────────────
  float gband = exp(-pow((uv.y - 0.30)*7.0,2.0));
  vec3 glowCol = mix(vec3(0.9,0.35,0.05), vec3(1.0,0.85,0.50), cycle);
  col += glowCol * gband * 0.18 * smoothstep(0.0, 0.3, cycle);

  // ── Dust motes / golden particles ────────────────────────────────────
  for(int di=0;di<12;di++){
    float fi = float(di);
    float dx = fract(hash2f(vec2(fi,0.0)) + t*0.006*(0.4+hash2f(vec2(fi,1.0))*0.6));
    float dy = 0.18 + hash2f(vec2(fi,2.0))*0.25 + sin(t*0.5+fi*1.9)*0.012;
    dx += mx.x*1.2;
    float dd = length(uv - vec2(dx, dy));
    float bright = (0.5 + 0.5*sin(t*1.8+fi*2.1)) * cycle;
    col += vec3(1.0,0.80,0.40) * bright * exp(-dd*dd*4000.0) * 0.6;
  }

  // ── Vignette ─────────────────────────────────────────────────────────
  vec2 vUvC = uv - 0.5;
  float vig = 1.0 - dot(vUvC*1.1, vUvC*1.1);
  col *= clamp(vig*1.15, 0.0, 1.0);

  gl_FragColor = vec4(max(col, vec3(0.0)), 1.0);
}
`;

// ─── Bloom downsample ────────────────────────────────────────────────────────

const BLOOM_DOWN_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uTex;
uniform vec2 uRes;
varying vec2 vUv;
void main(){
  vec2 tx = 1.0/uRes;
  vec4 c = texture2D(uTex, vUv)*4.0;
  c += texture2D(uTex, vUv+vec2( tx.x, tx.y));
  c += texture2D(uTex, vUv+vec2(-tx.x, tx.y));
  c += texture2D(uTex, vUv+vec2( tx.x,-tx.y));
  c += texture2D(uTex, vUv+vec2(-tx.x,-tx.y));
  c += texture2D(uTex, vUv+vec2( tx.x*2.0,0.0));
  c += texture2D(uTex, vUv+vec2(-tx.x*2.0,0.0));
  c += texture2D(uTex, vUv+vec2(0.0, tx.y*2.0));
  c += texture2D(uTex, vUv+vec2(0.0,-tx.y*2.0));
  gl_FragColor = c/13.0;
}`;

// ─── Bloom upsample ──────────────────────────────────────────────────────────

const BLOOM_UP_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uTex;
uniform sampler2D uPrev;
uniform vec2 uRes;
uniform float uStrength;
varying vec2 vUv;
void main(){
  vec2 tx=1.0/uRes;
  vec4 c  = texture2D(uTex,vUv+vec2(-tx.x, tx.y))*1.0;
  c += texture2D(uTex,vUv+vec2(0.0, tx.y))*2.0;
  c += texture2D(uTex,vUv+vec2( tx.x, tx.y))*1.0;
  c += texture2D(uTex,vUv+vec2(-tx.x,0.0))*2.0;
  c += texture2D(uTex,vUv)*4.0;
  c += texture2D(uTex,vUv+vec2( tx.x,0.0))*2.0;
  c += texture2D(uTex,vUv+vec2(-tx.x,-tx.y))*1.0;
  c += texture2D(uTex,vUv+vec2(0.0,-tx.y))*2.0;
  c += texture2D(uTex,vUv+vec2( tx.x,-tx.y))*1.0;
  c /= 16.0;
  gl_FragColor = texture2D(uPrev,vUv) + c*uStrength;
}`;

// ─── Composite ───────────────────────────────────────────────────────────────

const COMPOSITE_FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uScene;
uniform sampler2D uBloom;
uniform float uExposure;
varying vec2 vUv;
vec3 aces(vec3 x){
  float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14;
  return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.0,1.0);
}
void main(){
  vec3 scene = texture2D(uScene,vUv).rgb;
  vec3 bloom = texture2D(uBloom,vUv).rgb;
  vec3 col = scene + bloom*0.28;
  col = aces(col*uExposure);
  col = pow(col, vec3(1.0/2.2));
  gl_FragColor = vec4(col,1.0);
}`;

// ─── Wisp overlay ────────────────────────────────────────────────────────────

const WISP_FRAG = /* glsl */ `
precision highp float;
uniform vec2  uMouse;
uniform float uTime;
uniform vec2  uRes;
varying vec2  vUv;
void main(){
  vec2 m  = uMouse*0.5+0.5;
  float asp = uRes.x/uRes.y;
  vec2 uv = vUv;
  uv.x *= asp;
  vec2 mp = m;
  mp.x *= asp;
  float d = length(uv-mp);
  // warm golden wisp for sunrise
  float glow = exp(-d*d*20.0)*0.50;
  float ring = smoothstep(0.06,0.055,d)*smoothstep(0.04,0.05,d)*0.35;
  vec3 col = vec3(1.0,0.75,0.30)*glow + vec3(1.0,0.6,0.2)*ring;
  for(int i=0;i<6;i++){
    float fi=float(i);
    float ang = uTime*1.1+fi*1.047;
    float r = 0.022+fi*0.009;
    vec2 mp2 = mp+vec2(cos(ang)*r,sin(ang)*r*0.55);
    float dd = length(uv-mp2);
    col += vec3(1.0,0.7,0.3)*exp(-dd*dd*1100.0)*0.55;
  }
  gl_FragColor = vec4(col, min(1.0,glow*2.0+ring));
}`;

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeQuad() {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(
    new Float32Array([-1,-1,0, 1,-1,0, 1,1,0, -1,-1,0, 1,1,0, -1,1,0]), 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(
    new Float32Array([0,0, 1,0, 1,1, 0,0, 1,1, 0,1]), 2));
  return geo;
}

function makeRT(w, h) {
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

// ─── init ─────────────────────────────────────────────────────────────────────

export function init(canvas, container) {
  const renderer = new THREE.WebGLRenderer({
    canvas, antialias: false, alpha: false,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
  renderer.autoClear = false;
  renderer.setClearColor(0x000000, 1);

  const scene  = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  let W = 0, H = 0;
  let mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  let clock  = 0;
  let rafId  = null;
  let hidden = false;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let RT = {};
  function allocRT(w, h) {
    Object.values(RT).forEach(t => t?.dispose?.());
    RT = {};
    RT.scene = makeRT(w, h);
    for (let i = 0; i < 8; i++) {
      const d = Math.pow(2, i + 1);
      RT[`d${i}`] = makeRT(Math.max(1, Math.floor(w/d)), Math.max(1, Math.floor(h/d)));
      RT[`u${i}`] = makeRT(Math.max(1, Math.floor(w/d)), Math.max(1, Math.floor(h/d)));
    }
  }

  const quadGeo = makeQuad();

  const sceneMat = new THREE.RawShaderMaterial({
    vertexShader: VERT, fragmentShader: SCENE_FRAG,
    uniforms: {
      uTime:  { value: 0 },
      uRes:   { value: new THREE.Vector2(1, 1) },
      uMouse: { value: new THREE.Vector2(0, 0) },
    },
    depthTest: false, depthWrite: false,
  });

  const downMats = [], upMats = [];
  for (let i = 0; i < 8; i++) {
    downMats.push(new THREE.RawShaderMaterial({
      vertexShader: VERT, fragmentShader: BLOOM_DOWN_FRAG,
      uniforms: { uTex: { value: null }, uRes: { value: new THREE.Vector2() } },
      depthTest: false, depthWrite: false,
    }));
    upMats.push(new THREE.RawShaderMaterial({
      vertexShader: VERT, fragmentShader: BLOOM_UP_FRAG,
      uniforms: {
        uTex: { value: null }, uPrev: { value: null },
        uRes: { value: new THREE.Vector2() }, uStrength: { value: 0.50 },
      },
      depthTest: false, depthWrite: false,
    }));
  }

  const compositeMat = new THREE.RawShaderMaterial({
    vertexShader: VERT, fragmentShader: COMPOSITE_FRAG,
    uniforms: {
      uScene:    { value: null },
      uBloom:    { value: null },
      uExposure: { value: 1.0 },
    },
    depthTest: false, depthWrite: false,
  });

  const wispMat = new THREE.RawShaderMaterial({
    vertexShader: VERT, fragmentShader: WISP_FRAG,
    uniforms: {
      uMouse: { value: new THREE.Vector2(0, 0) },
      uTime:  { value: 0 },
      uRes:   { value: new THREE.Vector2(1, 1) },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthTest: false, depthWrite: false,
  });

  const mesh = new THREE.Mesh(quadGeo, sceneMat);
  scene.add(mesh);

  function resize() {
    const rect = container.getBoundingClientRect();
    W = Math.floor(rect.width  * Math.min(window.devicePixelRatio, 1.8));
    H = Math.floor(rect.height * Math.min(window.devicePixelRatio, 1.8));
    if (W < 1 || H < 1) return;
    renderer.setSize(rect.width, rect.height, false);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    allocRT(W, H);
    sceneMat.uniforms.uRes.value.set(W, H);
    wispMat.uniforms.uRes.value.set(W, H);
    for (let i = 0; i < 8; i++) {
      const d = Math.pow(2, i + 1);
      const bW = Math.max(1, Math.floor(W/d));
      const bH = Math.max(1, Math.floor(H/d));
      downMats[i].uniforms.uRes.value.set(bW, bH);
      upMats[i].uniforms.uRes.value.set(bW, bH);
    }
  }

  function onPointer(e) {
    const rect = container.getBoundingClientRect();
    const cx = e.touches ? e.touches[0].clientX : e.clientX;
    const cy = e.touches ? e.touches[0].clientY : e.clientY;
    mouse.tx = ((cx - rect.left) / rect.width)  * 2 - 1;
    mouse.ty = -(((cy - rect.top)  / rect.height) * 2 - 1);
  }

  function pass(mat, target) {
    mesh.material = mat;
    renderer.setRenderTarget(target || null);
    renderer.render(scene, camera);
  }

  function renderPost() {
    for (let i = 0; i < 8; i++) {
      const src = i === 0 ? RT.scene : RT[`d${i-1}`];
      downMats[i].uniforms.uTex.value = src.texture;
      pass(downMats[i], RT[`d${i}`]);
    }
    for (let i = 7; i >= 0; i--) {
      upMats[i].uniforms.uTex.value  = RT[`d${i}`].texture;
      upMats[i].uniforms.uPrev.value = (i === 7 ? RT[`d${7}`] : RT[`u${i+1}`]).texture;
      pass(upMats[i], RT[`u${i}`]);
    }
    compositeMat.uniforms.uScene.value = RT.scene.texture;
    compositeMat.uniforms.uBloom.value = RT.u0.texture;
    pass(compositeMat, null);
    wispMat.uniforms.uMouse.value.set(mouse.x, mouse.y);
    pass(wispMat, null);
  }

  let lastTime = performance.now();
  function frame(ts) {
    rafId = requestAnimationFrame(frame);
    if (hidden) return;
    const dt = Math.min((ts - lastTime) / 1000, 0.05);
    lastTime = ts;
    if (!reducedMotion) clock += dt;
    mouse.x += (mouse.tx - mouse.x) * 0.05;
    mouse.y += (mouse.ty - mouse.y) * 0.05;

    sceneMat.uniforms.uTime.value = clock;
    sceneMat.uniforms.uMouse.value.set(mouse.x, mouse.y);
    wispMat.uniforms.uTime.value  = clock;

    mesh.material = sceneMat;
    renderer.setRenderTarget(RT.scene);
    renderer.render(scene, camera);
    renderPost();
  }

  const ro = new ResizeObserver(() => resize());
  ro.observe(container);
  resize();

  window.addEventListener('mousemove', onPointer, { passive: true });
  window.addEventListener('touchmove', onPointer, { passive: true });
  document.addEventListener('visibilitychange', () => { hidden = document.hidden; });

  canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); cancelAnimationFrame(rafId); });
  canvas.addEventListener('webglcontextrestored', () => { resize(); rafId = requestAnimationFrame(frame); });

  rafId = requestAnimationFrame(frame);

  return function dispose() {
    cancelAnimationFrame(rafId);
    ro.disconnect();
    window.removeEventListener('mousemove', onPointer);
    window.removeEventListener('touchmove', onPointer);
    sceneMat.dispose();
    compositeMat.dispose();
    wispMat.dispose();
    downMats.forEach(m => m.dispose());
    upMats.forEach(m => m.dispose());
    quadGeo.dispose();
    Object.values(RT).forEach(t => t?.dispose?.());
    renderer.dispose();
  };
}
