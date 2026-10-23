/**
 * TempleNightScene.jsx
 * React lifecycle host for the Temple Night procedural Three.js renderer.
 *
 * Usage:
 *   import { TempleNightScene } from './effects/temple-night/TempleNightScene';
 *   import './effects/temple-night/styles.css';
 *
 *   <div className="effect-frame" style={{ height: '480px' }}>
 *     <TempleNightScene />
 *   </div>
 */

import { useEffect, useRef } from 'react';
import { init } from './templeNightRenderer';
import './styles.css';

export function TempleNightScene() {
  const canvasRef    = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const canvas    = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Guard against environments without WebGL
    const ctx = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!ctx) {
      console.warn('[TempleNightScene] WebGL not supported — skipping renderer.');
      return;
    }

    const dispose = init(canvas, container);
    return () => dispose();
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}
      aria-hidden="true"
    >
      <canvas
        ref={canvasRef}
        className="temple-night-canvas"
      />
    </div>
  );
}
