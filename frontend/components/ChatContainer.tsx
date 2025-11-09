import React, { useState, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { GenerateContentResponse } from "@google/genai";
import Button from './Button';
import Input from './Input';
import MessageBubble from './MessageBubble';
import LoadingSpinner from './LoadingSpinner';
import * as geminiService from '../services/geminiService';
import { fileToBase64, getUserLocation } from '../services/fileUtils';
import { 
  ChatMessage, 
  MessageRole, 
  FilePart, 
  Coordinates, 
  ReasoningStep, 
  CulturalContext // New import
} from '../types';
import { 
  GEMINI_MODEL_FLASH, 
  GEMINI_MODEL_PRO, 
  GEMINI_MODEL_FLASH_LITE,
  MOST_COMMON_MODELS, 
} from '../constants';
import EnhancedThinkingVisualization from './EnhancedThinkingVisualization'; // New import - though it's used in MessageBubble, not directly here.

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>(GEMINI_MODEL_FLASH);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [thinkingMode, setThinkingMode] = useState<boolean>(false);
  const [useGoogleSearch, setUseGoogleSearch] = useState<boolean>(false);
  const [useGoogleMaps, setUseGoogleMaps] = useState<boolean>(false);
  const [userLocation, setUserLocation] = useState<Coordinates | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
        setSelectedFile(file);
      } else {
        alert('Please upload an image or video file.');
        setSelectedFile(null);
      }
    } else {
      setSelectedFile(null);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prevMessages) => [...prevMessages, message]);
    setTimeout(scrollToBottom, 0);
  }, []);

  const updateLastMessage = useCallback((newParts: any[], metadataUpdates?: Partial<ChatMessage['metadata']>) => {
    setMessages((prevMessages) => {
      const lastMessageIndex = prevMessages.length - 1;
      if (lastMessageIndex >= 0 && prevMessages[lastMessageIndex].role === MessageRole.MODEL) {
        const updatedMessage = {
          ...prevMessages[lastMessageIndex],
          parts: newParts,
          metadata: {
            ...prevMessages[lastMessageIndex].metadata,
            ...metadataUpdates,
            isLoading: false,
          },
        };
        return prevMessages.map((msg, idx) => (idx === lastMessageIndex ? updatedMessage : msg));
      }
      return prevMessages;
    });
    setTimeout(scrollToBottom, 0);
  }, []);

  const fetchUserLocation = useCallback(async () => {
    if (userLocation) return;
    try {
      const location = await getUserLocation();
      setUserLocation(location);
      setLocationError(null);
    } catch (err: any) {
      setLocationError(`Error getting location: ${err.message}. Maps grounding might not work.`);
      console.error(err);
    }
  }, [userLocation]);

  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputMessage.trim() && !selectedFile) return;

    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: MessageRole.USER,
      parts: [],
      timestamp: new Date(),
    };

    if (inputMessage.trim()) {
      userMessage.parts.push({ text: inputMessage });
    }
    if (selectedFile) {
      userMessage.parts.push({
        image: selectedFile.type.startsWith('image/') ? (await fileToBase64(selectedFile)) : undefined,
        video: selectedFile.type.startsWith('video/') ? URL.createObjectURL(selectedFile) : undefined, // Display video via URL. Base64 sent to API.
      });
    }
    addMessage(userMessage);

    const modelResponsePlaceholder: ChatMessage = {
      id: uuidv4(),
      role: MessageRole.MODEL,
      parts: [{ text: '' }],
      timestamp: new Date(),
      metadata: {
        model: selectedModel,
        thinkingMode: thinkingMode && selectedModel === GEMINI_MODEL_PRO,
        isLoading: true,
      },
    };
    addMessage(modelResponsePlaceholder);

    try {
      let filePart: FilePart | undefined;
      if (selectedFile) {
        filePart = {
          type: selectedFile.type.startsWith('image/') ? 'image' : 'video',
          mimeType: selectedFile.type,
          base64Data: await fileToBase64(selectedFile),
        };
      }

      let geminiResponse: GenerateContentResponse;
      let groundingUrls: string[] = []; // This needs to be populated from geminiResponse if available
      let thinkingProcessData: { steps: ReasoningStep[]; context: CulturalContext } | undefined; // Declare for thinking process

      if (useGoogleMaps) {
        if (!userLocation) {
          await fetchUserLocation(); // Try to fetch location if not available
          if (!userLocation) { // If still not available, throw error
            throw new Error('Geolocation required for Maps grounding, but not available.');
          }
        }
        geminiResponse = await geminiService.generateContentWithGoogleMaps(
          selectedModel,
          inputMessage,
          userLocation!,
        );
        // Extract Maps grounding URLs if present
        if (geminiResponse.candidates?.[0]?.groundingMetadata?.groundingChunks) {
          groundingUrls = geminiResponse.candidates[0].groundingMetadata.groundingChunks
            .filter((chunk: any) => chunk.maps?.uri)
            .map((chunk: any) => chunk.maps.uri);
        }
      } else if (useGoogleSearch) {
        geminiResponse = await geminiService.generateContentWithGoogleSearch(
          selectedModel,
          inputMessage,
        );
        // Extract Search grounding URLs if present
        if (geminiResponse.candidates?.[0]?.groundingMetadata?.groundingChunks) {
          groundingUrls = geminiResponse.candidates[0].groundingMetadata.groundingChunks
            .filter((chunk: any) => chunk.web?.uri)
            .map((chunk: any) => chunk.web.uri);
        }
      } else {
        geminiResponse = await geminiService.generateContent(
          selectedModel,
          inputMessage,
          filePart,
          thinkingMode,
        );

        // Mock thinking process data if thinkingMode is active for Pro model
        if (thinkingMode && selectedModel === GEMINI_MODEL_PRO) {
          thinkingProcessData = {
            steps: [
              {
                type: "Knowledge Retrieval & Synthesis",
                action: "Querying Pan-African Knowledge Fabric for relevant concepts and remedies based on user input.",
                culturalContext: "Prioritizing information from specified or inferred cultural contexts (e.g., Yoruba, Swahili) while adhering to CARE principles.",
                culturalSources: ["Ifá Oracle", "Oral Tradition Archives", "Community Knowledge Nodes"],
                confidence: 95,
                careValidated: true,
                symbolicLogic: "MATCH (n:Concept|Remedy)-[r:RELATES_TO|ORIGINATES_FROM]->(c:Culture {name: 'Yoruba'}) WHERE n.name CONTAINS 'herb' RETURN n",
                careBreakdown: {
                  collectiveBenefit: { score: 0.90, explanation: "Ensuring knowledge benefit returns to the originating community." },
                  authorityControl: { score: 0.88, explanation: "Validating FPIC for data usage from community archives." },
                  responsibility: { score: 0.92, explanation: "Tracing provenance to ensure correct attribution and ethical data handling." },
                  ethics: { score: 0.93, explanation: "Adhering to indigenous data sovereignty principles for all retrieved knowledge." }
                }
              },
              {
                type: "CARE Principle Validation",
                action: "Performing real-time audit of retrieved knowledge for FPIC, permission levels, and community governance.",
                culturalContext: "Ensuring all knowledge shared aligns with Indigenous data sovereignty and community-approved protocols.",
                culturalSources: ["GRID Protocol Enforcer", "CARE Compliance Engine"],
                confidence: 98,
                careValidated: true,
                symbolicLogic: "CALL grid.validate_care_access({node_id: 'knowledge_node_xyz'})",
                careBreakdown: {
                  collectiveBenefit: { score: 0.95, explanation: "Confirming that sharing this information contributes to community well-being." },
                  authorityControl: { score: 0.91, explanation: "Verifying explicit community permission for the specific use case." },
                  responsibility: { score: 0.96, explanation: "Documenting all access and usage for audit trails and accountability." },
                  ethics: { score: 0.98, explanation: "Upholding sacred knowledge protection and cultural integrity." }
                }
              },
              {
                type: "Multi-Agent Consensus (Simulated)",
                action: "Consulting with 'Yoruba Healer AI' and 'Igbo Diagnosis AI' for cross-cultural validation and safety.",
                culturalContext: "Leveraging distributed intelligence within the Agent Mesh to provide a holistic and validated response.",
                culturalSources: ["Yoruba Healer AI Log", "Igbo Diagnosis AI Report"],
                confidence: 90,
                careValidated: true, // Assuming consensus reached and validated
                symbolicLogic: "CALL grid.initiate_reasoning({query: 'user_query', agents: ['yoruba-healer-001', 'igbo-diagnosis-001']})",
                careBreakdown: {
                  collectiveBenefit: { score: 0.85, explanation: "Seeking multi-perspective input to maximize collective benefit and safety." },
                  authorityControl: { score: 0.89, explanation: "Agents operating under delegated authority from their respective communities." },
                  responsibility: { score: 0.90, explanation: "Each agent takes responsibility for their contribution to the consensus." },
                  ethics: { score: 0.88, explanation: "Ensuring cross-cultural sensitivity and preventing misinterpretation." }
                }
              }
            ],
            context: {
              careScore: Math.round(((0.90 + 0.95 + 0.85) / 3) * 100), // Average of a few scores for mock
              culturalAccuracy: Math.round(((95 + 98 + 90) / 3)), // Average confidence
            }
          };
        }
      }

      const responseText = geminiResponse.text;
      // FIX: Declare responseParts here so it's accessible throughout the try block.
      // Initialize with the text response as it's always expected.
      const responseParts: any[] = [{ text: responseText }];

      // If video analysis, update parts with video file (if provided) and text
      if (filePart?.type === 'video' && filePart.base64Data) {
        // Here, we re-use the user's uploaded video for display if the model response is just text analysis.
        // If the model itself generates a video, we'd process that base64 here.
        // For simplicity, we assume text response for video analysis.
        // If it was a model-generated image/video, the response would have inlineData.
        const modelGeneratedImage = geminiResponse.candidates?.[0]?.content?.parts?.[0]?.inlineData;
        if (modelGeneratedImage && modelGeneratedImage.mimeType.startsWith('image/')) {
          responseParts.push({ image: modelGeneratedImage.data });
        }
      }

      updateLastMessage(responseParts, {
        rawResponse: geminiResponse,
        searchGrounding: useGoogleSearch ? groundingUrls : undefined,
        mapsGrounding: useGoogleMaps ? groundingUrls : undefined,
        thinkingProcess: thinkingProcessData, // Pass thinking process data
      });

    } catch (err: any) {
      console.error('Gemini API Error:', err);
      updateLastMessage([{ text: 'Oops! Something went wrong. Please try again.' }], { error: err.message });
      // Reset API key status if it's a "Requested entity not found." error
      if (err.message && err.message.includes("Requested entity was not found.")) {
        if (typeof window.aistudio !== 'undefined' && typeof window.aistudio.openSelectKey === 'function') {
           window.aistudio.openSelectKey(); // Prompt user to re-select key
        }
      }
    } finally {
      setIsLoading(false);
      setInputMessage('');
      handleRemoveFile(); // Clear selected file after sending
    }
  }, [inputMessage, selectedFile, selectedModel, thinkingMode, useGoogleSearch, useGoogleMaps, userLocation, addMessage, updateLastMessage, fetchUserLocation]);

  return (
    <div className="flex flex-col h-full bg-background rounded-lg shadow-custom overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-textSecondary text-lg mt-8">
            Start a conversation with Gemini!
            <br />
            You can ask questions, upload images or videos, use search or maps grounding, or enable thinking mode.
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && <LoadingSpinner />}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 bg-card border-t border-border sticky bottom-0">
        {selectedFile && (
          <div className="flex items-center space-x-2 p-2 bg-gray-100 rounded-md mb-2">
            <span className="text-sm text-gray-700">
              {selectedFile.type.startsWith('image/') ? 'Image' : 'Video'}: {selectedFile.name}
            </span>
            <Button type="button" onClick={handleRemoveFile} variant="ghost" size="small">
              X
            </Button>
          </div>
        )}

        {locationError && (
          <p className="text-red-500 text-sm mb-2">{locationError}</p>
        )}

        <div className="flex flex-wrap items-center gap-2 mb-4">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="p-2 border border-gray-300 rounded-md bg-white text-sm"
            disabled={isLoading}
          >
            {MOST_COMMON_MODELS.map((modelName) => (
              <option key={modelName} value={modelName}>
                {modelName.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ')}
              </option>
            ))}
          </select>

          <label className="flex items-center cursor-pointer text-sm text-gray-700">
            <input
              type="checkbox"
              className="form-checkbox h-4 w-4 text-primary rounded"
              checked={thinkingMode}
              onChange={(e) => setThinkingMode(e.target.checked)}
              disabled={isLoading || selectedModel !== GEMINI_MODEL_PRO}
            />
            <span className="ml-2">Thinking Mode (Pro only)</span>
          </label>

          <label className="flex items-center cursor-pointer text-sm text-gray-700">
            <input
              type="checkbox"
              className="form-checkbox h-4 w-4 text-primary rounded"
              checked={useGoogleSearch}
              onChange={(e) => {
                setUseGoogleSearch(e.target.checked);
                if (e.target.checked) setUseGoogleMaps(false); // Exclusive
              }}
              disabled={isLoading}
            />
            <span className="ml-2">Google Search</span>
          </label>

          <label className="flex items-center cursor-pointer text-sm text-gray-700">
            <input
              type="checkbox"
              className="form-checkbox h-4 w-4 text-primary rounded"
              checked={useGoogleMaps}
              onChange={(e) => {
                setUseGoogleMaps(e.target.checked);
                if (e.target.checked) {
                  setUseGoogleSearch(false); // Exclusive
                  fetchUserLocation(); // Request location when enabling Maps
                }
              }}
              disabled={isLoading}
            />
            <span className="ml-2">Google Maps</span>
          </label>
        </div>

        <div className="flex space-x-2">
          <label htmlFor="file-upload" className="cursor-pointer bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors duration-200 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-4 3 3 5-5V15z" clipRule="evenodd" />
            </svg>
            Attach
          </label>
          <input
            id="file-upload"
            type="file"
            accept="image/*,video/*"
            className="hidden"
            onChange={handleFileChange}
            disabled={isLoading}
          />

          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-3 border rounded-md"
            disabled={isLoading}
          />
          <Button type="submit" isLoading={isLoading} disabled={isLoading || (!inputMessage.trim() && !selectedFile)}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatContainer;