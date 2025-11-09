import React from 'react';
import ReactMarkdown, { type Components } from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { 
  ChatMessage, 
  MessageRole,
} from '../types';
import EnhancedThinkingVisualization from './EnhancedThinkingVisualization'; 

interface MessageBubbleProps {
  message: ChatMessage;
}

interface CodeProps extends React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> {
  node?: any; 
  inline?: boolean; 
  className?: string; 
  children: React.ReactNode; 
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === MessageRole.USER;
  const bubbleClasses = isUser
    ? 'bg-blue-500 text-white rounded-br-none self-end'
    : 'bg-card text-textPrimary rounded-bl-none self-start shadow-md';
  const avatar = isUser ? '😀' : '🧠';

  return (
    <div className={`flex items-start gap-2 max-w-[80%] mx-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <div className="p-2 text-2xl">{avatar}</div>}
      <div className={`p-4 rounded-xl mb-4 break-words ${bubbleClasses}`}>
        {message.parts.map((part, index) => (
          <div key={index}>
            {part.text && (
              <ReactMarkdown
                components={{
                  // FIX: Exclude the `ref` prop explicitly when passing `restProps` to `SyntaxHighlighter`
                  // to prevent a type incompatibility error as `SyntaxHighlighter` expects a different `ref` type.
                  code({ inline, className, children, ...restProps }: CodeProps) { 
                    const match = /language-(\w+)/.exec(className || '');
                    // Destructure `ref` to prevent it from being passed to SyntaxHighlighter
                    const { ref, ...rest } = restProps;

                    return !inline && match ? ( 
                      <SyntaxHighlighter
                        style={oneDark as any} 
                        language={match[1]}
                        PreTag="div" 
                        {...rest} // Pass the rest of the props, excluding `ref`
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      // FIX: Use `rest` instead of `restProps` to avoid passing the problematic `ref` to the native `code` element.
                      <code className={className} {...rest}>
                        {children}
                      </code>
                    );
                  },
                  pre: ({ children }) => <pre className="p-2 rounded-md bg-gray-800 text-white text-sm overflow-x-auto my-2">{children}</pre>,
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-200 underline hover:text-blue-100">{children}</a>,
                  li: ({ children }) => <li className="mb-1">{children}</li>,
                }}
              >
                {part.text}
              </ReactMarkdown>
            )}
            {part.image && (
              <img
                src={`data:image/jpeg;base64,${part.image}`}
                alt="Uploaded content"
                className="max-w-full h-auto rounded-lg mt-2 shadow-sm"
              />
            )}
            {part.video && (
              <video
                src={part.video}
                controls
                className="max-w-full h-auto rounded-lg mt-2 shadow-sm"
              >
                Your browser does not support the video tag.
              </video>
            )}
            {part.audio && (
              <audio
                src={`data:audio/mp3;base64,${part.audio}`} 
                controls
                className="w-full mt-2"
              >
                Your browser does not support the audio tag.
              </audio>
            )}
          </div>
        ))}
        {message.metadata?.isLoading && <div className="text-sm text-gray-400">Thinking...</div>}
        {message.metadata?.error && (
          <div className="text-sm text-red-300">Error: {message.metadata.error}</div>
        )}
        {message.metadata?.searchGrounding && message.metadata.searchGrounding.length > 0 && (
          <div className="mt-2 text-xs text-blue-200">
            <strong>Sources:</strong>
            <ul className="list-disc pl-4">
              {message.metadata.searchGrounding.map((url, i) => (
                <li key={i}>
                  <a href={url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {new URL(url).hostname}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
         {message.metadata?.mapsGrounding && message.metadata.mapsGrounding.length > 0 && (
          <div className="mt-2 text-xs text-blue-200">
            <strong>Places:</strong>
            <ul className="list-disc pl-4">
              {message.metadata.mapsGrounding.map((url, i) => (
                <li key={i}>
                  <a href={url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {new URL(url).hostname}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
         {message.metadata?.thinkingMode && (
          <div className="mt-2 text-xs text-gray-400">
            (Thinking Mode: 🧠🧠🧠 - using extended reasoning budget)
          </div>
        )}

        {/* New: CARE compliance summary display */}
        {message.metadata?.thinkingProcess && (
          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md text-sm text-green-800 flex items-center justify-between">
            <div className="flex items-center">
              <i className="fas fa-certificate text-green-600 mr-2"></i>
              <span>Overall CARE Compliance: <strong>{message.metadata.thinkingProcess.context.careScore}%</strong></span>
            </div>
            <span className="text-xs text-gray-600">Cultural Accuracy: {message.metadata.thinkingProcess.context.culturalAccuracy}%</span>
          </div>
        )}

        {/* New: Render EnhancedThinkingVisualization if thinking process data exists */}
        {message.metadata?.thinkingProcess && (
          <EnhancedThinkingVisualization 
            reasoningSteps={message.metadata.thinkingProcess.steps} 
            culturalContext={message.metadata.thinkingProcess.context} 
          />
        )}
      </div>
      {isUser && <div className="p-2 text-2xl">{avatar}</div>}
    </div>
  );
};

export default MessageBubble;