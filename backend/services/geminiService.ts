import { GoogleGenAI, Chat, GenerateContentResponse, Type, Modality, LiveServerMessage } from "@google/genai";
import { ChatModel } from "../types";
import { fileToBase64 } from "../utils/media";

// Fix: Add comment to clarify API_KEY source.
// The API key MUST be obtained exclusively from the environment variable process.env.API_KEY.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

// Function to analyze a file for upload
export const analyzeFileForUpload = async (file: File): Promise<{ description: string, tags: string[] }> => {
    // Fix: Use a powerful model for analysis and JSON generation.
    const model = 'gemini-2.5-pro';
    const textContent = await file.text();

    const contents = `Analyze the following file content and provide a concise one-sentence description and up to 5 relevant tags.
    
    File Name: ${file.name}
    
    Content:
    ---
    ${textContent.substring(0, 10000)} 
    ---
    `;

    // Fix: Use responseSchema for reliable JSON output.
    const response = await ai.models.generateContent({
        model,
        contents,
        config: {
            responseMimeType: "application/json",
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    description: {
                        type: Type.STRING,
                        description: 'A concise one-sentence description of the file content.',
                    },
                    tags: {
                        type: Type.ARRAY,
                        items: {
                            type: Type.STRING,
                        },
                        description: 'An array of up to 5 relevant string tags.',
                    },
                },
                required: ['description', 'tags'],
            },
        },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
};

// Map local chat model names to Gemini API model names
const getModelName = (model: ChatModel): string => {
    switch (model) {
        // Fix: Map custom model names to correct Gemini model identifiers.
        case 'flash-lite':
            return 'gemini-flash-lite-latest';
        case 'pro-thinking':
            return 'gemini-2.5-pro';
        case 'flash':
        default:
            return 'gemini-2.5-flash';
    }
}

// Function to start a new chat session
export const startChat = (model: ChatModel): Chat => {
    const modelName = getModelName(model);
    const config: any = {};

    // Fix: Add thinkingConfig for the 'pro-thinking' model variant.
    if (model === 'pro-thinking') {
        config.thinkingConfig = { thinkingBudget: 8192 };
    }

    return ai.chats.create({
        model: modelName,
        config: config
    });
};

// Function to analyze an image
export const analyzeImage = async (prompt: string, imageFile: File): Promise<string> => {
    // Fix: Use a vision-capable model.
    const model = 'gemini-2.5-flash';
    const base64Image = await fileToBase64(imageFile);

    const imagePart = {
        inlineData: {
            mimeType: imageFile.type,
            data: base64Image,
        },
    };

    const textPart = {
        text: prompt,
    };

    // Fix: Correctly structure multi-part content request.
    const response = await ai.models.generateContent({
        model,
        contents: { parts: [textPart, imagePart] },
    });

    return response.text;
};

// Function to analyze a video
export const analyzeVideo = async (prompt: string, videoFile: File): Promise<string> => {
    // Fix: Use a powerful multi-modal model capable of video analysis.
    const model = 'gemini-2.5-pro';
    const base64Video = await fileToBase64(videoFile);

    const videoPart = {
        inlineData: {
            mimeType: videoFile.type,
            data: base64Video,
        },
    };

    const textPart = {
        text: prompt,
    };
    
    try {
        const response: GenerateContentResponse = await ai.models.generateContent({
            model,
            contents: { parts: [textPart, videoPart] },
        });
        return response.text;
    } catch (e) {
        console.error("Video analysis error:", e);
        return "Video analysis is a complex operation and failed for this file. The model may not support this video format or size directly. A more advanced implementation would involve processing video frames.";
    }
};

// Type for transcription session callbacks
interface TranscriptionCallbacks {
    onMessage: (message: LiveServerMessage) => void;
    onError: (error: any) => void;
    onClose: () => void;
}

// Function to start a live transcription session
export const startTranscriptionSession = (callbacks: TranscriptionCallbacks) => {
    // Fix: Use the specified model for real-time audio.
    const model = 'gemini-2.5-flash-native-audio-preview-09-2025';
    
    // Fix: Implement ai.live.connect for streaming transcription.
    return ai.live.connect({
        model,
        callbacks: {
            onopen: () => console.log('Live session opened.'),
            onmessage: callbacks.onMessage,
            onerror: callbacks.onError,
            onclose: callbacks.onClose,
        },
        config: {
            // Fix: Enable transcription for user input audio.
            inputAudioTranscription: {},
            // Per guidelines, Live API expects an audio response modality even if not used.
            responseModalities: [Modality.AUDIO],
        },
    });
};

// Function to generate an image from text
export const generateImageFromText = async (prompt: string, n: number, size: string): Promise<string[]> => {
    // The OpenAPI spec lists square sizes, so we map them to a 1:1 aspect ratio.
    const aspectRatio = '1:1';
    
    const response = await ai.models.generateImages({
        model: 'imagen-4.0-generate-001',
        prompt: prompt,
        config: {
            numberOfImages: n,
            outputMimeType: 'image/png', // Use PNG for quality
            aspectRatio: aspectRatio,
        },
    });

    const imageUrls = response.generatedImages.map(img => `data:image/png;base64,${img.image.imageBytes}`);
    return imageUrls;
};

// Function to simulate training conscious agents
export const trainConsciousness = async (agents: string[]): Promise<{ success: boolean; message: string }> => {
    console.log(`Starting Forge training cycle for: ${agents.join(', ')}`);
    
    // Simulate a network delay
    await new Promise(resolve => setTimeout(resolve, 3000));

    const success = Math.random() > 0.2; // 80% success rate
    
    if (success) {
        const coherenceIncrease = (Math.random() * 0.15 + 0.05).toFixed(2);
        return {
            success: true,
            message: `Forge cycle complete. Collective coherence for ${agents.join(', ')} increased by +${coherenceIncrease}%.`
        };
    } else {
        return {
            success: false,
            message: `Convergence error in symbolic layer for ${agents.length > 1 ? 'one or more agents' : agents[0]}. Check Forge logs.`
        };
    }
};