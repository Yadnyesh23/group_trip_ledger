/**
 * MountainSunriseScene.jsx
 * React lifecycle host for the Mountain Sunrise procedural renderer.
 *
 * Usage:
 *   import { MountainSunriseScene } from './effects/mountain-sunrise/MountainSunriseScene';
 *
 *   <div style={{ height: '100%' }}>
 *     <MountainSunriseScene />
 *   </div>
 */

import { useEffect, useRef } from 'react';
import { init } from './mountainSunriseRenderer';

export function MountainSunriseScene() {
  const canvasRef    = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const canvas    = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!ctx) {
      console.warn('[MountainSunriseScene] WebGL not supported — skipping renderer.');
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
        className="temple-night-canvas" /* reuse same sizing rules */
      />
    </div>
  );
}
