/**
 * Athena visualization state modes
 */
export type OrbMode = 'idle' | 'listening' | 'thinking' | 'speaking';

/**
 * Audio analysis data extracted from Web Audio API
 */
export interface AudioData {
  /** Overall amplitude (0-1) */
  amplitude: number;
  /** Frequency band energies */
  frequencyBands: {
    bass: number;      // 20-250 Hz
    mid: number;       // 250-2000 Hz
    treble: number;    // 2000-20000 Hz
  };
  /** Raw frequency data for detailed analysis */
  frequencyData: Uint8Array;
  /** Raw time domain data (waveform) */
  timeDomainData: Uint8Array;
  /** Voice activity detection flag */
  isVoiceActive: boolean;
}

/**
 * Particle state for visualization
 */
export interface Particle {
  x: number;
  y: number;
  z: number;
  baseX: number;
  baseY: number;
  baseZ: number;
  velocity: { x: number; y: number; z: number };
  size: number;
  alpha: number;
  hue: number;
}

/**
 * Configuration for the particle orb
 */
export interface ParticleOrbConfig {
  /** Number of particles */
  particleCount: number;
  /** Base orb radius in pixels */
  baseRadius: number;
  /** Particle size range */
  particleSize: { min: number; max: number };
  /** Animation speed multiplier */
  speed: number;
}

/**
 * Props for the ParticleOrb component
 */
export interface ParticleOrbProps {
  /** Current visualization mode */
  mode: OrbMode;
  /** Optional audio data for real-time visualization */
  audioData?: AudioData | null;
  /** Canvas width */
  width?: number;
  /** Canvas height */
  height?: number;
  /** Custom configuration */
  config?: Partial<ParticleOrbConfig>;
}
