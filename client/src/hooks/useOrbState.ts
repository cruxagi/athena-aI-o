import { useState, useCallback, useEffect, useRef } from 'react';
import type { OrbMode } from '../types';

interface UseOrbStateOptions {
  /** Timeout in ms before returning to idle from listening (no voice) */
  listeningTimeout?: number;
  /** Timeout in ms before returning to idle from thinking */
  thinkingTimeout?: number;
  /** Enable auto-transition from listening to idle */
  autoIdle?: boolean;
}

interface UseOrbStateReturn {
  /** Current orb mode */
  mode: OrbMode;
  /** Set mode directly */
  setMode: (mode: OrbMode) => void;
  /** Transition to listening mode */
  startListening: () => void;
  /** Stop listening and return to idle */
  stopListening: () => void;
  /** Transition to thinking mode */
  startThinking: () => void;
  /** Transition to speaking mode */
  startSpeaking: () => void;
  /** Stop speaking and return to idle */
  stopSpeaking: () => void;
  /** Reset to idle */
  reset: () => void;
  /** Update based on voice activity */
  updateVoiceActivity: (isActive: boolean) => void;
}

const DEFAULT_OPTIONS: Required<UseOrbStateOptions> = {
  listeningTimeout: 2000,
  thinkingTimeout: 30000,
  autoIdle: true,
};

/**
 * State machine hook for managing orb visualization modes
 */
export function useOrbState(
  options: UseOrbStateOptions = {}
): UseOrbStateReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  const [mode, setModeState] = useState<OrbMode>('idle');
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastVoiceActivityRef = useRef<number>(0);

  // Clear any pending timeouts
  const clearTimeouts = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  // Set mode with timeout management
  const setMode = useCallback((newMode: OrbMode) => {
    clearTimeouts();
    setModeState(newMode);
  }, [clearTimeouts]);

  // Start listening mode
  const startListening = useCallback(() => {
    clearTimeouts();
    setModeState('listening');
    lastVoiceActivityRef.current = Date.now();

    if (opts.autoIdle) {
      timeoutRef.current = setTimeout(() => {
        setModeState('idle');
      }, opts.listeningTimeout);
    }
  }, [clearTimeouts, opts.autoIdle, opts.listeningTimeout]);

  // Stop listening
  const stopListening = useCallback(() => {
    clearTimeouts();
    setModeState('idle');
  }, [clearTimeouts]);

  // Start thinking mode
  const startThinking = useCallback(() => {
    clearTimeouts();
    setModeState('thinking');

    // Safety timeout to prevent stuck in thinking state
    timeoutRef.current = setTimeout(() => {
      setModeState('idle');
    }, opts.thinkingTimeout);
  }, [clearTimeouts, opts.thinkingTimeout]);

  // Start speaking mode
  const startSpeaking = useCallback(() => {
    clearTimeouts();
    setModeState('speaking');
  }, [clearTimeouts]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    clearTimeouts();
    setModeState('idle');
  }, [clearTimeouts]);

  // Reset to idle
  const reset = useCallback(() => {
    clearTimeouts();
    setModeState('idle');
  }, [clearTimeouts]);

  // Update based on voice activity detection
  const updateVoiceActivity = useCallback((isActive: boolean) => {
    if (mode !== 'listening') return;

    if (isActive) {
      lastVoiceActivityRef.current = Date.now();
      clearTimeouts();

      if (opts.autoIdle) {
        // Reset timeout
        timeoutRef.current = setTimeout(() => {
          setModeState('idle');
        }, opts.listeningTimeout);
      }
    }
  }, [mode, clearTimeouts, opts.autoIdle, opts.listeningTimeout]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimeouts();
    };
  }, [clearTimeouts]);

  return {
    mode,
    setMode,
    startListening,
    stopListening,
    startThinking,
    startSpeaking,
    stopSpeaking,
    reset,
    updateVoiceActivity,
  };
}

/**
 * State machine for push-to-talk mode
 */
export function usePushToTalk(
  onRecordingStart?: () => void,
  onRecordingEnd?: (duration: number) => void
): {
  isRecording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
  toggleRecording: () => void;
} {
  const [isRecording, setIsRecording] = useState(false);
  const startTimeRef = useRef<number | null>(null);

  const startRecording = useCallback(() => {
    if (!isRecording) {
      startTimeRef.current = Date.now();
      setIsRecording(true);
      onRecordingStart?.();
    }
  }, [isRecording, onRecordingStart]);

  const stopRecording = useCallback(() => {
    if (isRecording && startTimeRef.current) {
      const duration = Date.now() - startTimeRef.current;
      setIsRecording(false);
      startTimeRef.current = null;
      onRecordingEnd?.(duration);
    }
  }, [isRecording, onRecordingEnd]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return {
    isRecording,
    startRecording,
    stopRecording,
    toggleRecording,
  };
}
