import React, { useState, useRef, useEffect, useCallback } from 'react';
import { LiveServerMessage } from '@google/genai';
import Button from './Button';
import LoadingSpinner from './LoadingSpinner';
import * as geminiService from '../services/geminiService';
import { decodeAudioData, decodeBase64, createAudioBlob } from '../services/audioUtils';
import {
  AUDIO_SAMPLE_RATE,
  AUDIO_OUTPUT_SAMPLE_RATE,
  LIVE_AUDIO_MIME_TYPE,
  GEMINI_MODEL_LIVE_AUDIO,
} from '../constants';

// Define AudioContexts outside component to persist across renders
let inputAudioContext: AudioContext | null = null;
let outputAudioContext: AudioContext | null = null;
let scriptProcessor: ScriptProcessorNode | null = null;
let mediaStreamSource: MediaStreamAudioSourceNode | null = null;
let streamRef: React.MutableRefObject<MediaStream | null> = { current: null };
let nextStartTime = 0; // Tracks the end of the audio playback queue
const sources = new Set<AudioBufferSourceNode>(); // Track active audio sources for interruption

const LiveConversationPanel: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentInputTranscription, setCurrentInputTranscription] = useState('');
  const [currentOutputTranscription, setCurrentOutputTranscription] = useState('');
  const [conversationHistory, setConversationHistory] = useState<string[]>([]);

  const sessionPromiseRef = useRef<Promise<Awaited<ReturnType<typeof geminiService.connectLiveSession>>> | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const resetAudioContexts = useCallback(() => {
    if (scriptProcessor) {
      scriptProcessor.disconnect();
      scriptProcessor.onaudioprocess = null;
      scriptProcessor = null;
    }
    if (mediaStreamSource) {
      mediaStreamSource.disconnect();
      mediaStreamSource = null;
    }
    if (inputAudioContext) {
      inputAudioContext.close();
      inputAudioContext = null;
    }
    if (outputAudioContext) {
      outputAudioContext.close();
      outputAudioContext = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    // Stop all playing audio sources
    for (const source of sources.values()) {
      try {
        source.stop();
      } catch (e) {
        console.warn("Error stopping audio source:", e);
      }
      sources.delete(source);
    }
    nextStartTime = 0;
  }, []);

  const startLiveSession = useCallback(async () => {
    setIsConnecting(true);
    setError(null);
    setConversationHistory([]);
    setCurrentInputTranscription('');
    setCurrentOutputTranscription('');
    resetAudioContexts(); // Ensure a clean state

    try {
      // Request microphone access
      streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Initialize audio contexts
      inputAudioContext = new AudioContext({ sampleRate: AUDIO_SAMPLE_RATE });
      outputAudioContext = new AudioContext({ sampleRate: AUDIO_OUTPUT_SAMPLE_RATE });

      const onMessage = async (message: LiveServerMessage) => {
        // Handle input transcription
        if (message.serverContent?.inputTranscription) {
          setCurrentInputTranscription((prev) => prev + message.serverContent!.inputTranscription!.text);
        }
        // Handle output transcription
        if (message.serverContent?.outputTranscription) {
          setCurrentOutputTranscription((prev) => prev + message.serverContent!.outputTranscription!.text);
        }
        // Handle turn complete
        if (message.serverContent?.turnComplete) {
          if (currentInputTranscription || currentOutputTranscription) { // Only add if there's actual transcription
             setConversationHistory(prev => [
                ...prev,
                `You: ${currentInputTranscription}`,
                `AI: ${currentOutputTranscription}`
             ]);
          }
          setCurrentInputTranscription('');
          setCurrentOutputTranscription('');
        }

        // Handle model's audio output
        const base64EncodedAudioString = message.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
        if (base64EncodedAudioString && outputAudioContext) {
          nextStartTime = Math.max(nextStartTime, outputAudioContext.currentTime);
          const audioBuffer = await decodeAudioData(
            decodeBase64(base64EncodedAudioString),
            outputAudioContext,
            AUDIO_OUTPUT_SAMPLE_RATE,
            1, // Assuming mono channel
          );
          const source = outputAudioContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(outputAudioContext.destination);
          source.addEventListener('ended', () => {
            sources.delete(source);
          });
          source.start(nextStartTime);
          nextStartTime += audioBuffer.duration;
          sources.add(source);
        }

        // Handle interruptions (stop current audio playback)
        const interrupted = message.serverContent?.interrupted;
        if (interrupted) {
          for (const source of sources.values()) {
            source.stop();
            sources.delete(source);
          }
          nextStartTime = 0;
        }
      };

      sessionPromiseRef.current = geminiService.connectLiveSession({
        onopen: () => {
          console.debug('Live session opened');
          setIsRecording(true); // Start recording once session is open
          setIsConnecting(false);

          // Connect microphone to scriptProcessor
          if (inputAudioContext && streamRef.current) {
            mediaStreamSource = inputAudioContext.createMediaStreamSource(streamRef.current);
            scriptProcessor = inputAudioContext.createScriptProcessor(4096, 1, 1); // Buffer size, input channels, output channels
            scriptProcessor.onaudioprocess = (audioProcessingEvent) => {
              const inputData = audioProcessingEvent.inputBuffer.getChannelData(0);
              const pcmBlob = createAudioBlob(inputData);
              // CRITICAL: Solely rely on sessionPromise resolves and then call `session.sendRealtimeInput`, **do not** add other condition checks.
              // Fix: Wrap the audio blob in a `media` object as required by `sendRealtimeInput`.
              sessionPromiseRef.current?.then((session) => {
                session.sendRealtimeInput({ media: pcmBlob });
              });
            };
            mediaStreamSource.connect(scriptProcessor);
            scriptProcessor.connect(inputAudioContext.destination); // Required for scriptProcessor to function
          }
        },
        onmessage: onMessage,
        onerror: (e: ErrorEvent) => {
          console.error('Live session error:', e);
          setError(`Live session error: ${e.message}`);
          setIsConnecting(false);
          setIsRecording(false);
          resetAudioContexts();
        },
        onclose: (e: CloseEvent) => {
          console.debug('Live session closed', e);
          setIsConnecting(false);
          setIsRecording(false);
          if (!e.wasClean) {
            setError(`Live session closed with error: ${e.code} - ${e.reason}`);
          }
          resetAudioContexts();
        },
      }, "You are a helpful assistant for cultural knowledge about African traditions. Adhere to CARE principles and ensure data sovereignty when discussing sensitive topics.");

    } catch (err: any) {
      console.error('Failed to start live session:', err);
      setError(`Failed to access microphone or start session: ${err.message}`);
      setIsConnecting(false);
      setIsRecording(false);
      resetAudioContexts();
    }
  }, [resetAudioContexts, currentInputTranscription, currentOutputTranscription]);

  const stopLiveSession = useCallback(async () => {
    if (sessionPromiseRef.current) {
      try {
        const session = await sessionPromiseRef.current;
        session.close();
      } catch (err) {
        console.error('Error closing live session:', err);
      } finally {
        sessionPromiseRef.current = null;
      }
    }
    setIsRecording(false);
    setIsConnecting(false);
    resetAudioContexts();
  }, [resetAudioContexts]);

  useEffect(() => {
    // Clean up on component unmount
    return () => {
      stopLiveSession();
    };
  }, [stopLiveSession]);

  return (
    <div className="flex flex-col h-full p-4 md:p-8 max-w-2xl mx-auto bg-card rounded-lg shadow-custom space-y-6">
      <h2 className="text-3xl font-bold text-center text-primary">Live AI Conversation</h2>
      <p className="text-center text-textSecondary">
        Engage in real-time voice conversations with Gemini Native Audio.
      </p>

      <div className="flex justify-center gap-4">
        {!isRecording ? (
          <Button onClick={startLiveSession} isLoading={isConnecting} disabled={isConnecting}>
            {isConnecting ? 'Connecting...' : 'Start Conversation'}
          </Button>
        ) : (
          <Button onClick={stopLiveSession} variant="danger" disabled={isConnecting}>
            Stop Conversation
          </Button>
        )}
      </div>

      {error && <p className="text-red-500 text-center">{error}</p>}
      {isConnecting && <LoadingSpinner />}

      <div className="flex-1 overflow-y-auto bg-background p-4 rounded-md border border-border flex flex-col-reverse max-h-[400px]">
        {conversationHistory.slice().reverse().map((turn, index) => (
          <div key={index} className={`py-1 ${turn.startsWith('You:') ? 'text-blue-700' : 'text-gray-800'}`}>
            <span className="font-semibold">{turn.split(':')[0]}:</span> {turn.split(':').slice(1).join(':')}
          </div>
        ))}
        {currentOutputTranscription && (
          <div className="py-1 text-gray-800 animate-pulse">
            <span className="font-semibold">AI (typing):</span> {currentOutputTranscription}...
          </div>
        )}
        {currentInputTranscription && (
          <div className="py-1 text-blue-700 animate-pulse">
            <span className="font-semibold">You (speaking):</span> {currentInputTranscription}...
          </div>
        )}
        {isRecording && !currentInputTranscription && !currentOutputTranscription && (
             <div className="py-1 text-gray-500 text-center">
                Listening...
            </div>
        )}
      </div>

      <div className="text-sm text-textSecondary text-center">
        Model: {GEMINI_MODEL_LIVE_AUDIO} (Real-time audio, input & output transcription enabled)
      </div>
    </div>
  );
};

export default LiveConversationPanel;