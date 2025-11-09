import React, { useState, useCallback, useRef } from 'react';
import Button from './Button';
import LoadingSpinner from './LoadingSpinner';
import * as geminiService from '../services/geminiService';
import { AUDIO_OUTPUT_SAMPLE_RATE } from '../constants';
import { decodeAudioData, decodeBase64 } from '../services/audioUtils';

// AudioContext needs to be created once and shared.
let outputAudioContext: AudioContext | null = null;
let currentSource: AudioBufferSourceNode | null = null;

const TTSPanel: React.FC = () => {
  const [textToSpeak, setTextToSpeak] = useState('Say cheerfully: Have a wonderful day!');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleGenerateSpeech = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    if (currentSource) {
      currentSource.stop();
      currentSource = null;
    }

    try {
      const base64Audio = await geminiService.generateSpeech(textToSpeak);

      // Initialize AudioContext if not already done
      if (!outputAudioContext) {
        outputAudioContext = new AudioContext({
          sampleRate: AUDIO_OUTPUT_SAMPLE_RATE,
        });
      }

      const audioBuffer = await decodeAudioData(
        decodeBase64(base64Audio),
        outputAudioContext,
        AUDIO_OUTPUT_SAMPLE_RATE,
        1, // Assuming mono channel
      );

      // Play audio using Web Audio API for better control
      currentSource = outputAudioContext.createBufferSource();
      currentSource.buffer = audioBuffer;
      currentSource.connect(outputAudioContext.destination);
      currentSource.start(0);

    } catch (err: any) {
      console.error('TTS Error:', err);
      setError(`Failed to generate speech: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [textToSpeak]);

  // Clean up AudioContext on component unmount
  React.useEffect(() => {
    return () => {
      if (currentSource) {
        currentSource.stop();
        currentSource = null;
      }
      if (outputAudioContext) {
        outputAudioContext.close();
        outputAudioContext = null;
      }
    };
  }, []);

  return (
    <div className="flex flex-col p-4 md:p-8 max-w-xl mx-auto bg-card rounded-lg shadow-custom space-y-6">
      <h2 className="text-3xl font-bold text-center text-primary">Text-to-Speech</h2>
      <p className="text-center text-textSecondary">
        Convert any text into natural-sounding speech using Gemini's TTS model.
      </p>

      <textarea
        value={textToSpeak}
        onChange={(e) => setTextToSpeak(e.target.value)}
        rows={8}
        placeholder="Enter text to convert to speech..."
        className="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary text-textPrimary resize-y"
        disabled={isLoading}
      ></textarea>

      <Button onClick={handleGenerateSpeech} isLoading={isLoading} disabled={!textToSpeak.trim()}>
        Generate Speech
      </Button>

      {isLoading && <LoadingSpinner />}
      {error && <p className="text-red-500 text-center">{error}</p>}

      <div className="mt-4 p-3 bg-background rounded-md border border-border text-sm text-textSecondary">
        <p><strong>Model:</strong> gemini-2.5-flash-preview-tts</p>
        <p><strong>Default Voice:</strong> Zephyr</p>
      </div>
    </div>
  );
};

export default TTSPanel;