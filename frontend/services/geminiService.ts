import { GoogleGenAI, GenerateContentResponse, LiveServerMessage } from "@google/genai";
import {
  GEMINI_MODEL_FLASH,
  GEMINI_MODEL_PRO,
  GEMINI_MODEL_TTS,
  GEMINI_MODEL_LIVE_AUDIO,
  LIVE_AUDIO_RESPONSE_MODALITY,
  TTS_RESPONSE_MODALITY,
} from '../constants';
import { FilePart, Coordinates } from '../types';
import { createAudioBlob } from './audioUtils';
import { fileToBase64 } from './fileUtils'; // Import fileToBase64

let aiInstance: GoogleGenAI | null = null;

// Ensure this function is called before any Gemini API interaction
export async function getGeminiClient(): Promise<GoogleGenAI> {
  if (aiInstance) {
    return aiInstance;
  }
  // The API key is injected automatically via process.env.API_KEY
  aiInstance = new GoogleGenAI({ apiKey: process.env.API_KEY });
  return aiInstance;
}

export async function initializeGeminiClient(): Promise<boolean> {
  // This function is mainly for showing the API key selection UI for Veo models.
  // We'll simulate success for other models, as the API key is expected to be present.
  if (typeof window.aistudio !== 'undefined' && typeof window.aistudio.hasSelectedApiKey === 'function') {
    const hasKey = await window.aistudio.hasSelectedApiKey();
    if (!hasKey) {
      await window.aistudio.openSelectKey();
      // Assume success after opening dialog for other models.
      // For Veo models, one would typically re-check hasSelectedApiKey() here,
      // but for simplicity and broader applicability, we proceed.
      return true;
    }
    return true;
  }
  // If aistudio is not available (e.g., local development), assume API_KEY is set via environment.
  console.warn("window.aistudio not found. Proceeding with API_KEY from environment.");
  return true;
}

export async function generateContent(
  model: string,
  prompt: string,
  filePart?: FilePart,
  thinkingMode: boolean = false
): Promise<GenerateContentResponse> {
  const ai = await getGeminiClient();

  const contents: Array<any> = [{ text: prompt }];
  if (filePart) {
    contents.unshift({
      inlineData: {
        mimeType: filePart.mimeType,
        data: filePart.base64Data,
      },
    });
  }

  const config: { [key: string]: any } = {};
  if (thinkingMode && model === GEMINI_MODEL_PRO) {
    config.thinkingConfig = { thinkingBudget: 32768 };
  }

  const response = await ai.models.generateContent({
    model,
    contents: { parts: contents },
    config,
  });
  return response;
}

export async function generateContentWithGoogleSearch(
  model: string,
  prompt: string,
): Promise<GenerateContentResponse> {
  const ai = await getGeminiClient();
  const response = await ai.models.generateContent({
    model,
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
    },
  });
  return response;
}

export async function generateContentWithGoogleMaps(
  model: string,
  prompt: string,
  userLocation: Coordinates,
): Promise<GenerateContentResponse> {
  const ai = await getGeminiClient();
  const response = await ai.models.generateContent({
    model,
    contents: prompt,
    config: {
      tools: [{ googleMaps: {} }],
      toolConfig: {
        retrievalConfig: {
          latLng: {
            latitude: userLocation.latitude,
            longitude: userLocation.longitude,
          },
        },
      },
    },
  });
  return response;
}

export async function generateSpeech(text: string, voiceName: string = 'Zephyr'): Promise<string> {
  const ai = await getGeminiClient();
  const response = await ai.models.generateContent({
    model: GEMINI_MODEL_TTS,
    contents: [{ parts: [{ text }] }],
    config: {
      responseModalities: TTS_RESPONSE_MODALITY,
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName },
        },
      },
    },
  });

  const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
  if (!base64Audio) {
    throw new Error('No audio data received from TTS.');
  }
  return base64Audio;
}

// Live Audio Conversation
export function connectLiveSession(
  callbacks: {
    onopen: () => void;
    onmessage: (message: LiveServerMessage) => void;
    onerror: (event: ErrorEvent) => void;
    onclose: (event: CloseEvent) => void;
  },
  systemInstruction?: string
) {
  return getGeminiClient().then((ai) => {
    return ai.live.connect({
      model: GEMINI_MODEL_LIVE_AUDIO,
      callbacks,
      config: {
        responseModalities: LIVE_AUDIO_RESPONSE_MODALITY,
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Zephyr' } }, // Default voice
        },
        systemInstruction: systemInstruction || 'You are a friendly and helpful assistant.',
        outputAudioTranscription: {}, // Enable transcription for model output
        inputAudioTranscription: {}, // Enable transcription for user input
      },
    });
  });
}

// Function to send audio to the live session
export async function sendAudioToLiveSession(
  sessionPromise: Promise<Awaited<ReturnType<GoogleGenAI['live']['connect']>>>,
  audioData: Float32Array
) {
  try {
    const session = await sessionPromise;
    const pcmBlob = createAudioBlob(audioData);
    session.sendRealtimeInput({ media: pcmBlob });
  } catch (error) {
    console.error('Error sending audio to live session:', error);
  }
}

// Mocked functions for new UI components
export async function trainConsciousness(agents: string[]): Promise<{ success: boolean; message: string; }> {
  console.log(`Simulating training for agents: ${agents.join(', ')}`);
  return new Promise(resolve => {
    setTimeout(() => {
      const success = Math.random() > 0.3; // Simulate occasional failure
      if (success) {
        resolve({ success: true, message: `Forge training cycle completed successfully for ${agents.length} agents.` });
      } else {
        resolve({ success: false, message: `Forge training failed for some agents. Check logs for details.` });
      }
    }, 3000); // Simulate network delay
  });
}

export async function analyzeFileForUpload(file: File): Promise<{ description: string; tags: string[]; }> {
  console.log(`Simulating AI analysis for file: ${file.name}`);
  // In a real scenario, you'd send the file's base64Data to Gemini for analysis.
  // const fileBase64 = await fileToBase64(file);
  // const ai = await getGeminiClient();
  // const response = await ai.models.generateContent({ ... });

  return new Promise(resolve => {
    setTimeout(() => {
      const description = `AI-generated summary of ${file.name}: This content discusses core principles of African Neuro-Symbolic AI, emphasizing cultural sovereignty and CARE principles. It highlights the Soul-Mind-Body architecture and the role of Ifá wisdom.`;
      const tags = ['consciousness', 'AIKS', 'Ifá', 'CARE', 'NeuroSymbolic', file.name.split('.').pop() || 'file'];
      resolve({ description, tags });
    }, 2500); // Simulate network delay
  });
}

// Vision Analysis: Analyze Image
export async function analyzeImage(prompt: string, file: File): Promise<string> {
  const ai = await getGeminiClient();
  const base64Data = await fileToBase64(file);
  
  const response = await ai.models.generateContent({
    model: GEMINI_MODEL_FLASH,
    contents: {
      role: 'user',
      parts: [
        {
          inlineData: {
            mimeType: file.type,
            data: base64Data,
          },
        },
        { text: prompt },
      ],
    },
  });

  return response.text || 'No response from the model.';
}

// Vision Analysis: Analyze Video
export async function analyzeVideo(prompt: string, file: File): Promise<string> {
  const ai = await getGeminiClient();
  const base64Data = await fileToBase64(file);
  
  const response = await ai.models.generateContent({
    model: GEMINI_MODEL_FLASH,
    contents: {
      role: 'user',
      parts: [
        {
          inlineData: {
            mimeType: file.type,
            data: base64Data,
          },
        },
        { text: prompt },
      ],
    },
  });

  return response.text || 'No response from the model.';
}