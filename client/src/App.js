import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { nord } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { User, Bot, Copy, Check, Send, Mic } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

const ChatMessage = ({ message, isStreaming }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  // Custom renderers for different markdown elements
  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      return !inline ? (
        <div className="my-4">
          <SyntaxHighlighter
            language={language}
            style={nord}
            PreTag="div"
            className="rounded-lg"
            {...props}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      ) : (
        <code className="bg-gray-100 px-1 rounded text-sm" {...props}>
          {children}
        </code>
      );
    },
    
    table({ children }) {
      return (
        <div className="my-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            {children}
          </table>
        </div>
      );
    },
    
    thead({ children }) {
      return <thead className="bg-gray-50">{children}</thead>;
    },
    
    th({ children }) {
      return (
        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          {children}
        </th>
      );
    },
    
    td({ children }) {
      return <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{children}</td>;
    },
    
    p({ children }) {
      return <p className="mb-4 last:mb-0">{children}</p>;
    },
    
    ul({ children }) {
      return <ul className="list-disc pl-6 mb-4">{children}</ul>;
    },
    
    ol({ children }) {
      return <ol className="list-decimal pl-6 mb-4">{children}</ol>;
    },
    
    h1({ children }) {
      return <h1 className="text-2xl font-bold mb-4">{children}</h1>;
    },
    
    h2({ children }) {
      return <h2 className="text-xl font-bold mb-3">{children}</h2>;
    },
    
    h3({ children }) {
      return <h3 className="text-lg font-bold mb-2">{children}</h3>;
    }
  };

  const showCopyButton = message.role === 'assistant' && !isStreaming;

  return (
    <div className="flex gap-3">
      <div className="flex gap-3 max-w-3xl flex-row">
        <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-gray-100">
          {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
        </div>
        <div className="flex flex-col relative w-full">
          <div className={`rounded-lg px-4 py-2 ${
            message.role === 'user' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-900'
          }`}>
            {showCopyButton && (
              <button
                onClick={handleCopy}
                className="absolute top-2 right-1 p-1 rounded-md hover:bg-gray-200 transition-colors"
                title={copied ? "Copied!" : "Copy to clipboard"}
              >
                {copied ? (
                  <Check size={16} className="text-green-600" />
                ) : (
                  <Copy size={16} className="text-gray-500" />
                )}
              </button>
            )}
            <div className="text-sm">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={components}
                className={`prose ${message.role === 'user' ? 'prose-invert' : ''} max-w-none`}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


const ChatUI = () => {
  const [messages, setMessages] = useState([{
    role: 'assistant', content: `**Welcome! I am a Q&A bot**\n\nI have access to the tools to fetch reddit threads for topics and summarize them.\n\n**Available Threads:**\nYou can fetch them using their name. Example: "Get me threads for ClaudeAI"\n\n- Artifical\n- Bard\n- ClaudeAI\n- Deep Learning\n- Javascript\n- LocalLamma\n- Machine Learning\n- OpenAI\n- Python\n- RAG\n- React\n- Singularity\n\n If it's a general question, use No tool: Questions \n\n Note that I **do not have chat history** as of now.`
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [conversationId] = useState(() => uuidv4());
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setInput(transcript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    } else {
      console.error('Speech recognition is not supported in this browser.');
    }
  }, []);

  const handleMicClick = () => {
    if (recognitionRef.current) {
      if (isRecording) {
        recognitionRef.current.stop();
      } else {
        recognitionRef.current.start();
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    abortControllerRef.current = new AbortController();

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage, { role: 'assistant', content: '' }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(process.env.REACT_APP_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input, conversation_id: conversationId }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
     
      const contentRef = { current: '' };
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        contentRef.current += chunk;
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = contentRef.current;
          return newMessages;
        });
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Error:', error);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request.'
        }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      
      <div className="flex-none p-4 border-b">
        <h1 className="text-xl font-semibold">Chat Assistant</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages?.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex-none p-4 border-t">
        <form onSubmit={handleSubmit} className="flex gap-2 items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleMicClick}
            className={`p-2 rounded-lg ${isRecording ? 'bg-red-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
            disabled={isLoading}
          >
            {isRecording ? (
              <div className="wave-container">
                <div className="wave"></div>
                <div className="wave"></div>
                <div className="wave"></div>
              </div>
            ) : (
              <Mic size={20} />
            )}
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatUI;