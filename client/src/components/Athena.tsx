import React, { useCallback, useEffect } from 'react';
import { ParticleOrb } from './ParticleOrb';
import { useAudioAnalyzer } from '../hooks/useAudioAnalyzer';
import { useOrbState, usePushToTalk } from '../hooks/useOrbState';
import type { OrbMode } from '../types';

interface AthenaProps {
  /** Optional callback when recording starts */
  onRecordingStart?: () => void;
  /** Optional callback when recording ends with audio data */
  onRecordingEnd?: (duration: number) => void;
  /** Optional callback when mode changes */
  onModeChange?: (mode: OrbMode) => void;
  /** Enable always-on listening mode (vs push-to-talk) */
  alwaysListening?: boolean;
  /** Size of the orb */
  size?: number;
}

/**
 * Athena - Main voice assistant component with particle visualization
 */
export const Athena: React.FC<AthenaProps> = ({
  onRecordingStart,
  onRecordingEnd,
  onModeChange,
  alwaysListening = false,
  size = 400,
}) => {
  // Audio analysis hook
  const {
    audioData,
    isActive: isMicActive,
    start: startMic,
    stop: stopMic,
    error: micError,
  } = useAudioAnalyzer();

  // Orb state machine
  const {
    mode,
    setMode,
    startListening,
    stopListening,
    startThinking,
    startSpeaking,
    stopSpeaking,
    updateVoiceActivity,
  } = useOrbState({ autoIdle: !alwaysListening });

  // Push-to-talk state
  const {
    isRecording,
    startRecording,
    stopRecording,
  } = usePushToTalk(onRecordingStart, onRecordingEnd);

  // Notify mode changes
  useEffect(() => {
    onModeChange?.(mode);
  }, [mode, onModeChange]);

  // Update voice activity for auto-idle
  useEffect(() => {
    if (audioData) {
      updateVoiceActivity(audioData.isVoiceActive);
    }
  }, [audioData, updateVoiceActivity]);

  // Handle mic activation with mode sync
  const handleMicStart = useCallback(async () => {
    await startMic();
    startListening();
    startRecording();
  }, [startMic, startListening, startRecording]);

  const handleMicStop = useCallback(() => {
    stopRecording();
    if (!alwaysListening) {
      stopMic();
      stopListening();
    }
  }, [stopMic, stopListening, stopRecording, alwaysListening]);

  // Toggle function for button
  const toggleListening = useCallback(async () => {
    if (isRecording) {
      handleMicStop();
    } else {
      await handleMicStart();
    }
  }, [isRecording, handleMicStart, handleMicStop]);

  // Keyboard shortcut (Space for push-to-talk)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat && !isRecording) {
        e.preventDefault();
        handleMicStart();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space' && isRecording) {
        e.preventDefault();
        handleMicStop();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isRecording, handleMicStart, handleMicStop]);

  // Demo mode buttons - simulates backend states
  const simulateThinking = useCallback(() => {
    startThinking();
    // Simulate thinking for 3 seconds then speak
    setTimeout(() => {
      startSpeaking();
      // Simulate speaking for 2 seconds then idle
      setTimeout(() => {
        stopSpeaking();
      }, 2000);
    }, 3000);
  }, [startThinking, startSpeaking, stopSpeaking]);

  return (
    <div className="athena-container">
      <div className="athena-orb-wrapper">
        <ParticleOrb
          mode={mode}
          audioData={audioData}
          width={size}
          height={size}
        />
      </div>

      <div className="athena-status">
        <span className={`status-indicator ${mode}`} />
        <span className="status-text">
          {mode === 'idle' && 'Ready'}
          {mode === 'listening' && 'Listening...'}
          {mode === 'thinking' && 'Processing...'}
          {mode === 'speaking' && 'Speaking...'}
        </span>
      </div>

      {micError && (
        <div className="athena-error">
          {micError}
        </div>
      )}

      <div className="athena-controls">
        <button
          className={`mic-button ${isRecording ? 'active' : ''}`}
          onClick={toggleListening}
          aria-label={isRecording ? 'Stop listening' : 'Start listening'}
        >
          <svg viewBox="0 0 24 24" width="32" height="32">
            <path
              fill="currentColor"
              d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 1.93c-3.94-.49-7-3.85-7-7.93h2c0 3.31 2.69 6 6 6s6-2.69 6-6h2c0 4.08-3.06 7.44-7 7.93V19h4v2H8v-2h4v-3.07z"
            />
          </svg>
        </button>

        <p className="athena-hint">
          {isRecording
            ? 'Release to send'
            : 'Hold space or click to speak'}
        </p>
      </div>

      {/* Demo controls for testing different states */}
      <div className="athena-demo-controls">
        <button onClick={() => setMode('idle')}>Idle</button>
        <button onClick={() => setMode('listening')}>Listen</button>
        <button onClick={() => setMode('thinking')}>Think</button>
        <button onClick={() => setMode('speaking')}>Speak</button>
        <button onClick={simulateThinking}>Demo Flow</button>
      </div>

      <style>{`
        .athena-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 2rem;
          background: linear-gradient(135deg, #0a0a0f 0%, #0d0d18 50%, #0a0a12 100%);
          color: #fff;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .athena-orb-wrapper {
          position: relative;
          margin-bottom: 2rem;
        }

        .athena-orb-wrapper::before {
          content: '';
          position: absolute;
          inset: -20px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(100, 150, 255, 0.1) 0%, transparent 70%);
          pointer-events: none;
        }

        .athena-status {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
          font-size: 1.125rem;
          color: #a0a0b0;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          transition: all 0.3s ease;
        }

        .status-indicator.idle {
          background: #4a5568;
          box-shadow: 0 0 8px rgba(74, 85, 104, 0.5);
        }

        .status-indicator.listening {
          background: #38b2ac;
          box-shadow: 0 0 12px rgba(56, 178, 172, 0.6);
          animation: pulse 1.5s ease-in-out infinite;
        }

        .status-indicator.thinking {
          background: #9f7aea;
          box-shadow: 0 0 12px rgba(159, 122, 234, 0.6);
          animation: pulse 0.8s ease-in-out infinite;
        }

        .status-indicator.speaking {
          background: #ecc94b;
          box-shadow: 0 0 12px rgba(236, 201, 75, 0.6);
          animation: pulse 0.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.7; }
        }

        .athena-error {
          color: #fc8181;
          background: rgba(252, 129, 129, 0.1);
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          margin-bottom: 1rem;
          font-size: 0.875rem;
        }

        .athena-controls {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .mic-button {
          width: 72px;
          height: 72px;
          border-radius: 50%;
          border: none;
          background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
          color: #a0aec0;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .mic-button:hover {
          background: linear-gradient(135deg, #3d4758 0%, #2a303c 100%);
          transform: scale(1.05);
        }

        .mic-button.active {
          background: linear-gradient(135deg, #38b2ac 0%, #2c7a7b 100%);
          color: #fff;
          box-shadow: 0 0 20px rgba(56, 178, 172, 0.4);
          animation: recording-pulse 1.5s ease-in-out infinite;
        }

        @keyframes recording-pulse {
          0%, 100% { box-shadow: 0 0 20px rgba(56, 178, 172, 0.4); }
          50% { box-shadow: 0 0 30px rgba(56, 178, 172, 0.6); }
        }

        .athena-hint {
          font-size: 0.875rem;
          color: #718096;
          margin: 0;
        }

        .athena-demo-controls {
          position: fixed;
          bottom: 1rem;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 0.5rem;
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.5);
          border-radius: 8px;
          backdrop-filter: blur(10px);
        }

        .athena-demo-controls button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          background: #2d3748;
          color: #a0aec0;
          font-size: 0.75rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .athena-demo-controls button:hover {
          background: #3d4758;
          color: #fff;
        }
      `}</style>
    </div>
  );
};

export default Athena;
