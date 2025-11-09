import { Modality } from "@google/genai";

export const GEMINI_MODEL_FLASH_LITE = 'gemini-flash-lite-latest';
export const GEMINI_MODEL_FLASH = 'gemini-2.5-flash';
export const GEMINI_MODEL_PRO = 'gemini-2.5-pro';
export const GEMINI_MODEL_TTS = 'gemini-2.5-flash-preview-tts';
export const GEMINI_MODEL_LIVE_AUDIO = 'gemini-2.5-flash-native-audio-preview-09-2025';

export const MOST_COMMON_MODELS = [
  GEMINI_MODEL_FLASH,
  GEMINI_MODEL_PRO,
  GEMINI_MODEL_FLASH_LITE,
];

export const AUDIO_SAMPLE_RATE = 16000;
export const AUDIO_OUTPUT_SAMPLE_RATE = 24000;
export const LIVE_AUDIO_MIME_TYPE = 'audio/pcm;rate=16000';
export const LIVE_AUDIO_RESPONSE_MODALITY = [Modality.AUDIO];
export const TTS_RESPONSE_MODALITY = [Modality.AUDIO];

export const BACKEND_API_BASE_URL = 'http://localhost:8000'; // Assuming FastAPI runs on 8000
export const AI_STUDIO_BILLING_DOCS_URL = 'ai.google.dev/gemini-api/docs/billing';
