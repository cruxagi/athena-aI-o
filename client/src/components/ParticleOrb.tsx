import React, { useEffect, useRef, useCallback } from 'react';
import type { OrbMode, AudioData, Particle, ParticleOrbConfig, ParticleOrbProps } from '../types';

const DEFAULT_CONFIG: ParticleOrbConfig = {
  particleCount: 1500,
  baseRadius: 120,
  particleSize: { min: 1, max: 3 },
  speed: 1,
};

// Color palettes for different modes (HSL)
const MODE_COLORS: Record<OrbMode, { hue: number; saturation: number; lightness: number }> = {
  idle: { hue: 220, saturation: 60, lightness: 50 },      // Calm blue
  listening: { hue: 180, saturation: 80, lightness: 55 }, // Cyan/teal
  thinking: { hue: 270, saturation: 70, lightness: 60 },  // Purple
  speaking: { hue: 45, saturation: 90, lightness: 55 },   // Golden/amber
};

// Mode-specific behavior parameters
const MODE_PARAMS: Record<OrbMode, {
  radiusScale: number;
  jitter: number;
  rotationSpeed: number;
  pulseSpeed: number;
  particleAlpha: number;
}> = {
  idle: {
    radiusScale: 0.9,
    jitter: 0.3,
    rotationSpeed: 0.1,
    pulseSpeed: 0.5,
    particleAlpha: 0.4,
  },
  listening: {
    radiusScale: 1.0,
    jitter: 0.8,
    rotationSpeed: 0.3,
    pulseSpeed: 1.5,
    particleAlpha: 0.7,
  },
  thinking: {
    radiusScale: 0.95,
    jitter: 1.5,
    rotationSpeed: 0.8,
    pulseSpeed: 3.0,
    particleAlpha: 0.6,
  },
  speaking: {
    radiusScale: 1.1,
    jitter: 1.0,
    rotationSpeed: 0.5,
    pulseSpeed: 2.0,
    particleAlpha: 0.85,
  },
};

/**
 * Creates particles distributed on a sphere using fibonacci lattice
 */
function createParticles(count: number, radius: number): Particle[] {
  const particles: Particle[] = [];
  const goldenRatio = (1 + Math.sqrt(5)) / 2;

  for (let i = 0; i < count; i++) {
    const theta = 2 * Math.PI * i / goldenRatio;
    const phi = Math.acos(1 - 2 * (i + 0.5) / count);

    const x = radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.sin(phi) * Math.sin(theta);
    const z = radius * Math.cos(phi);

    particles.push({
      x, y, z,
      baseX: x,
      baseY: y,
      baseZ: z,
      velocity: { x: 0, y: 0, z: 0 },
      size: 1 + Math.random() * 2,
      alpha: 0.5 + Math.random() * 0.5,
      hue: Math.random() * 30 - 15, // Slight hue variation
    });
  }

  return particles;
}

/**
 * ParticleOrb - Audio-reactive particle visualization component
 */
export const ParticleOrb: React.FC<ParticleOrbProps> = ({
  mode = 'idle',
  audioData = null,
  width = 400,
  height = 400,
  config = {},
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationRef = useRef<number | null>(null);
  const timeRef = useRef<number>(0);
  const modeTransitionRef = useRef<{ from: OrbMode; to: OrbMode; progress: number }>({
    from: mode,
    to: mode,
    progress: 1,
  });
  const prevModeRef = useRef<OrbMode>(mode);

  const cfg = { ...DEFAULT_CONFIG, ...config };

  // Initialize particles
  useEffect(() => {
    particlesRef.current = createParticles(cfg.particleCount, cfg.baseRadius);
  }, [cfg.particleCount, cfg.baseRadius]);

  // Handle mode transitions
  useEffect(() => {
    if (mode !== prevModeRef.current) {
      modeTransitionRef.current = {
        from: prevModeRef.current,
        to: mode,
        progress: 0,
      };
      prevModeRef.current = mode;
    }
  }, [mode]);

  // Interpolate between mode parameters
  const getModeParams = useCallback(() => {
    const transition = modeTransitionRef.current;
    if (transition.progress >= 1) {
      return MODE_PARAMS[transition.to];
    }

    const from = MODE_PARAMS[transition.from];
    const to = MODE_PARAMS[transition.to];
    const t = transition.progress;

    return {
      radiusScale: from.radiusScale + (to.radiusScale - from.radiusScale) * t,
      jitter: from.jitter + (to.jitter - from.jitter) * t,
      rotationSpeed: from.rotationSpeed + (to.rotationSpeed - from.rotationSpeed) * t,
      pulseSpeed: from.pulseSpeed + (to.pulseSpeed - from.pulseSpeed) * t,
      particleAlpha: from.particleAlpha + (to.particleAlpha - from.particleAlpha) * t,
    };
  }, []);

  // Get interpolated color
  const getModeColor = useCallback(() => {
    const transition = modeTransitionRef.current;
    if (transition.progress >= 1) {
      return MODE_COLORS[transition.to];
    }

    const from = MODE_COLORS[transition.from];
    const to = MODE_COLORS[transition.to];
    const t = transition.progress;

    return {
      hue: from.hue + (to.hue - from.hue) * t,
      saturation: from.saturation + (to.saturation - from.saturation) * t,
      lightness: from.lightness + (to.lightness - from.lightness) * t,
    };
  }, []);

  // Main render loop
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) {
      animationRef.current = requestAnimationFrame(render);
      return;
    }

    const particles = particlesRef.current;
    const params = getModeParams();
    const color = getModeColor();
    const time = timeRef.current;

    // Update transition progress
    if (modeTransitionRef.current.progress < 1) {
      modeTransitionRef.current.progress = Math.min(
        modeTransitionRef.current.progress + 0.02,
        1
      );
    }

    // Clear canvas with trail effect
    ctx.fillStyle = 'rgba(10, 10, 15, 0.15)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Audio-reactive parameters
    const amplitude = audioData?.amplitude ?? 0;
    const bass = audioData?.frequencyBands?.bass ?? 0;
    const mid = audioData?.frequencyBands?.mid ?? 0;
    const treble = audioData?.frequencyBands?.treble ?? 0;
    const isVoiceActive = audioData?.isVoiceActive ?? false;

    // Dynamic radius based on audio
    const audioRadius = 1 + amplitude * 0.3 + bass * 0.2;
    const effectiveRadius = cfg.baseRadius * params.radiusScale * audioRadius;

    // Global rotation
    const rotationAngle = time * params.rotationSpeed * cfg.speed * 0.001;
    const cosRot = Math.cos(rotationAngle);
    const sinRot = Math.sin(rotationAngle);

    // Pulse effect
    const pulse = Math.sin(time * params.pulseSpeed * cfg.speed * 0.002) * 0.1 + 1;

    // Sort particles by z-depth for proper rendering
    const sortedParticles = [...particles].sort((a, b) => a.z - b.z);

    for (const particle of sortedParticles) {
      // Apply jitter based on mode and audio
      const jitterAmount = params.jitter * (1 + amplitude * 2 + treble * 1.5);
      const jitterX = (Math.random() - 0.5) * jitterAmount;
      const jitterY = (Math.random() - 0.5) * jitterAmount;
      const jitterZ = (Math.random() - 0.5) * jitterAmount;

      // Calculate target position with audio reactivity
      const audioDisplace = isVoiceActive ? 1 + mid * 0.5 : 1;
      const targetX = particle.baseX * audioDisplace * pulse;
      const targetY = particle.baseY * audioDisplace * pulse;
      const targetZ = particle.baseZ * audioDisplace * pulse;

      // Smooth movement towards target
      particle.x += (targetX - particle.x) * 0.1 + jitterX;
      particle.y += (targetY - particle.y) * 0.1 + jitterY;
      particle.z += (targetZ - particle.z) * 0.1 + jitterZ;

      // Apply rotation around Y axis
      const rotatedX = particle.x * cosRot - particle.z * sinRot;
      const rotatedZ = particle.x * sinRot + particle.z * cosRot;

      // Scale factor for perspective
      const scale = effectiveRadius / cfg.baseRadius;
      const perspective = 400 / (400 + rotatedZ * scale);

      // Project to 2D
      const screenX = centerX + rotatedX * perspective * scale;
      const screenY = centerY + particle.y * perspective * scale;

      // Size based on depth, audio, and mode
      const depthSize = perspective * particle.size * (cfg.particleSize.max - cfg.particleSize.min) + cfg.particleSize.min;
      const audioSize = 1 + bass * 0.5 + amplitude * 0.3;
      const finalSize = depthSize * audioSize * scale;

      // Alpha based on depth and mode
      const depthAlpha = (perspective - 0.5) * 2;
      const finalAlpha = Math.max(0, Math.min(1,
        depthAlpha * params.particleAlpha * particle.alpha * (0.7 + amplitude * 0.3)
      ));

      // Color with particle variation and audio reactivity
      const hueShift = particle.hue + (treble * 30);
      const finalHue = (color.hue + hueShift + 360) % 360;
      const saturation = color.saturation + mid * 20;
      const lightness = color.lightness + amplitude * 15;

      // Draw particle
      ctx.beginPath();
      ctx.arc(screenX, screenY, finalSize, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${finalHue}, ${saturation}%, ${lightness}%, ${finalAlpha})`;
      ctx.fill();

      // Add glow for brighter particles
      if (finalAlpha > 0.6 && amplitude > 0.1) {
        ctx.beginPath();
        ctx.arc(screenX, screenY, finalSize * 2, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${finalHue}, ${saturation}%, ${lightness + 20}%, ${finalAlpha * 0.2})`;
        ctx.fill();
      }
    }

    // Draw central glow
    const glowRadius = effectiveRadius * 0.8 * (1 + amplitude * 0.5);
    const gradient = ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, glowRadius
    );
    gradient.addColorStop(0, `hsla(${color.hue}, ${color.saturation}%, ${color.lightness + 20}%, ${0.15 + amplitude * 0.1})`);
    gradient.addColorStop(0.5, `hsla(${color.hue}, ${color.saturation}%, ${color.lightness}%, ${0.05 + amplitude * 0.05})`);
    gradient.addColorStop(1, 'transparent');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Update time
    timeRef.current += 16; // Approximate 60fps

    animationRef.current = requestAnimationFrame(render);
  }, [audioData, cfg, getModeParams, getModeColor]);

  // Start/stop animation loop
  useEffect(() => {
    animationRef.current = requestAnimationFrame(render);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [render]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        display: 'block',
        borderRadius: '50%',
        background: 'radial-gradient(circle, #0d0d12 0%, #050508 100%)',
      }}
    />
  );
};

export default ParticleOrb;
