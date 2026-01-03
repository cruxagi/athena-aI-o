import { useEffect, useRef, useState, useCallback } from 'react';
import type { AudioData } from '../types';

interface UseAudioAnalyzerOptions {
  /** FFT size for frequency analysis (power of 2, 32-32768) */
  fftSize?: number;
  /** Smoothing time constant (0-1) */
  smoothingTimeConstant?: number;
  /** VAD threshold (0-1) */
  vadThreshold?: number;
  /** Update rate in ms */
  updateRate?: number;
}

interface UseAudioAnalyzerReturn {
  /** Current audio data */
  audioData: AudioData | null;
  /** Whether microphone is active */
  isActive: boolean;
  /** Start capturing audio */
  start: () => Promise<void>;
  /** Stop capturing audio */
  stop: () => void;
  /** Error message if any */
  error: string | null;
}

const DEFAULT_OPTIONS: Required<UseAudioAnalyzerOptions> = {
  fftSize: 256,
  smoothingTimeConstant: 0.8,
  vadThreshold: 0.02,
  updateRate: 16, // ~60fps
};

/**
 * Hook for capturing and analyzing microphone audio in real-time
 */
export function useAudioAnalyzer(
  options: UseAudioAnalyzerOptions = {}
): UseAudioAnalyzerReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  const [audioData, setAudioData] = useState<AudioData | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastUpdateRef = useRef<number>(0);

  const analyze = useCallback(() => {
    if (!analyserRef.current) return;

    const now = performance.now();
    if (now - lastUpdateRef.current < opts.updateRate) {
      animationFrameRef.current = requestAnimationFrame(analyze);
      return;
    }
    lastUpdateRef.current = now;

    const analyser = analyserRef.current;
    const frequencyData = new Uint8Array(analyser.frequencyBinCount);
    const timeDomainData = new Uint8Array(analyser.frequencyBinCount);

    analyser.getByteFrequencyData(frequencyData);
    analyser.getByteTimeDomainData(timeDomainData);

    // Calculate overall amplitude from time domain data
    let sum = 0;
    for (let i = 0; i < timeDomainData.length; i++) {
      const normalized = (timeDomainData[i] - 128) / 128;
      sum += normalized * normalized;
    }
    const amplitude = Math.sqrt(sum / timeDomainData.length);

    // Calculate frequency bands
    const binCount = frequencyData.length;
    const nyquist = (audioContextRef.current?.sampleRate || 44100) / 2;
    const binWidth = nyquist / binCount;

    // Bass: 20-250 Hz
    const bassEnd = Math.min(Math.floor(250 / binWidth), binCount);
    let bassSum = 0;
    for (let i = 0; i < bassEnd; i++) {
      bassSum += frequencyData[i];
    }
    const bass = bassEnd > 0 ? bassSum / (bassEnd * 255) : 0;

    // Mid: 250-2000 Hz
    const midStart = bassEnd;
    const midEnd = Math.min(Math.floor(2000 / binWidth), binCount);
    let midSum = 0;
    for (let i = midStart; i < midEnd; i++) {
      midSum += frequencyData[i];
    }
    const mid = midEnd > midStart ? midSum / ((midEnd - midStart) * 255) : 0;

    // Treble: 2000-20000 Hz
    const trebleStart = midEnd;
    let trebleSum = 0;
    for (let i = trebleStart; i < binCount; i++) {
      trebleSum += frequencyData[i];
    }
    const treble = binCount > trebleStart
      ? trebleSum / ((binCount - trebleStart) * 255)
      : 0;

    // Voice Activity Detection - focus on speech frequencies (300-3400 Hz)
    const vadStart = Math.floor(300 / binWidth);
    const vadEnd = Math.min(Math.floor(3400 / binWidth), binCount);
    let vadSum = 0;
    for (let i = vadStart; i < vadEnd; i++) {
      vadSum += frequencyData[i];
    }
    const vadLevel = vadEnd > vadStart
      ? vadSum / ((vadEnd - vadStart) * 255)
      : 0;
    const isVoiceActive = vadLevel > opts.vadThreshold;

    setAudioData({
      amplitude,
      frequencyBands: { bass, mid, treble },
      frequencyData: new Uint8Array(frequencyData),
      timeDomainData: new Uint8Array(timeDomainData),
      isVoiceActive,
    });

    animationFrameRef.current = requestAnimationFrame(analyze);
  }, [opts.updateRate, opts.vadThreshold]);

  const start = useCallback(async () => {
    try {
      setError(null);

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      streamRef.current = stream;

      // Create audio context and analyzer
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = opts.fftSize;
      analyser.smoothingTimeConstant = opts.smoothingTimeConstant;
      analyserRef.current = analyser;

      // Connect microphone to analyzer
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      setIsActive(true);

      // Start analysis loop
      animationFrameRef.current = requestAnimationFrame(analyze);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to access microphone';
      setError(message);
      console.error('Audio analyzer error:', err);
    }
  }, [analyze, opts.fftSize, opts.smoothingTimeConstant]);

  const stop = useCallback(() => {
    // Stop animation loop
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
    setIsActive(false);
    setAudioData(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  return {
    audioData,
    isActive,
    start,
    stop,
    error,
  };
}

/**
 * Hook for analyzing audio output (TTS/speaker)
 * Used for synchronizing visuals with speech output
 */
export function useOutputAudioAnalyzer(
  audioElement: HTMLAudioElement | null,
  options: UseAudioAnalyzerOptions = {}
): AudioData | null {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const [audioData, setAudioData] = useState<AudioData | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!audioElement) return;

    const audioContext = new AudioContext();
    audioContextRef.current = audioContext;

    const analyser = audioContext.createAnalyser();
    analyser.fftSize = opts.fftSize;
    analyser.smoothingTimeConstant = opts.smoothingTimeConstant;
    analyserRef.current = analyser;

    const source = audioContext.createMediaElementSource(audioElement);
    source.connect(analyser);
    analyser.connect(audioContext.destination);
    sourceRef.current = source;

    const analyze = () => {
      if (!analyserRef.current) return;

      const frequencyData = new Uint8Array(analyser.frequencyBinCount);
      const timeDomainData = new Uint8Array(analyser.frequencyBinCount);

      analyser.getByteFrequencyData(frequencyData);
      analyser.getByteTimeDomainData(timeDomainData);

      let sum = 0;
      for (let i = 0; i < timeDomainData.length; i++) {
        const normalized = (timeDomainData[i] - 128) / 128;
        sum += normalized * normalized;
      }
      const amplitude = Math.sqrt(sum / timeDomainData.length);

      setAudioData({
        amplitude,
        frequencyBands: { bass: 0, mid: 0, treble: 0 },
        frequencyData: new Uint8Array(frequencyData),
        timeDomainData: new Uint8Array(timeDomainData),
        isVoiceActive: amplitude > opts.vadThreshold,
      });

      animationFrameRef.current = requestAnimationFrame(analyze);
    };

    animationFrameRef.current = requestAnimationFrame(analyze);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      audioContext.close();
    };
  }, [audioElement, opts.fftSize, opts.smoothingTimeConstant, opts.vadThreshold]);

  return audioData;
}
