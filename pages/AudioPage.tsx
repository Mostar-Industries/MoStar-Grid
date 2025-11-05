import React, { useState, useRef, useEffect } from 'react';
import { LiveServerMessage } from "@google/genai";
import { startTranscriptionSession } from '../services/geminiService';
import { createBlob } from '../utils/media';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

interface AudioPageProps {
    isSentinelMode: boolean;
}

const AudioPage: React.FC<AudioPageProps> = ({ isSentinelMode }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [error, setError] = useState('');

    // FIX: Replaced non-exported `LiveSession` type with an inferred type using `ReturnType`.
    const sessionPromiseRef = useRef<ReturnType<typeof startTranscriptionSession> | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);

    const handleTranscriptionMessage = (message: LiveServerMessage) => {
        if (message.serverContent?.inputTranscription) {
            const text = message.serverContent.inputTranscription.text;
            setTranscript(prev => prev + text);
        }
        if (message.serverContent?.turnComplete) {
            setTranscript(prev => prev + '\n');
        }
    };
    
    const startRecording = async () => {
        if (isSentinelMode) return;
        setIsRecording(true);
        setTranscript('');
        setError('');
        try {
            mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
            // FIX: Property 'webkitAudioContext' does not exist on type 'Window & typeof globalThis'. Cast to `any` to allow fallback for older browsers.
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
            
            const source = audioContextRef.current.createMediaStreamSource(mediaStreamRef.current);
            scriptProcessorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1);
            
            scriptProcessorRef.current.onaudioprocess = (audioProcessingEvent) => {
                const inputData = audioProcessingEvent.inputBuffer.getChannelData(0);
                const pcmBlob = createBlob(inputData);
                sessionPromiseRef.current?.then((session) => {
                    session.sendRealtimeInput({ media: pcmBlob });
                });
            };

            source.connect(scriptProcessorRef.current);
            scriptProcessorRef.current.connect(audioContextRef.current.destination);

            sessionPromiseRef.current = startTranscriptionSession({
                onMessage: handleTranscriptionMessage,
                onError: (e) => {
                    console.error("Live session error:", e);
                    setError("A connection error occurred. Please try again.");
                    stopRecording();
                },
                onClose: () => console.log('Live session closed.')
            });

        } catch (err) {
            console.error("Failed to start recording:", err);
            setError("Could not access microphone. Please check permissions.");
            setIsRecording(false);
        }
    };
    
    const stopRecording = () => {
        setIsRecording(false);
        sessionPromiseRef.current?.then(session => session.close());
        sessionPromiseRef.current = null;
        
        mediaStreamRef.current?.getTracks().forEach(track => track.stop());
        scriptProcessorRef.current?.disconnect();
        
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
            audioContextRef.current.close();
        }
    };

    useEffect(() => {
        return () => { // Cleanup on component unmount
            if (isRecording) {
                stopRecording();
            }
        };
    }, [isRecording]);

    return (
        <div>
            <PageTitle title="Live Audio Transcription" />
            <div className="text-center mb-6">
                <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isSentinelMode}
                    className={`px-8 py-4 rounded-full font-bold text-lg transition-all ${isRecording ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse' : 'gradient-bg text-white hover:opacity-90'} disabled:bg-gray-600 disabled:cursor-not-allowed`}
                >
                    {isSentinelMode ? (
                        <>
                            <i className="fas fa-lock mr-2"></i> Audio Input Sealed
                        </>
                    ) : isRecording ? (
                        <>
                            <i className="fas fa-stop-circle mr-2"></i> Stop Transcription
                        </>
                    ) : (
                        <>
                            <i className="fas fa-microphone-alt mr-2"></i> Start Transcribing
                        </>
                    )}
                </button>
            </div>
            
             {error && <p className="text-red-400 text-center mb-4">{error}</p>}

            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 min-h-[400px]">
                <h3 className="text-lg font-bold text-white mb-2">Transcript</h3>
                {transcript ? (
                     <p className="text-gray-300 whitespace-pre-wrap">{transcript}</p>
                ) : (
                    <p className="text-gray-500">
                        {isSentinelMode
                            ? "Audio inputs are disabled in Sentinel Mode."
                            : 'Click "Start Transcribing" and begin speaking. The live transcript will appear here.'
                        }
                    </p>
                )}
            </div>
        </div>
    );
};

export default AudioPage;