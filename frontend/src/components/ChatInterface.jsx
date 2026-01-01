import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

export function ChatInterface({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load chat history
    const loadHistory = async () => {
      try {
        const response = await fetch(`/api/chat/history/${sessionId}`);
        if (response.ok) {
          const history = await response.json();
          setMessages(history.map(msg => ({
            role: msg.role,
            content: msg.content,
            sources: msg.sources || []
          })));
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
      }
    };
    loadHistory();
  }, [sessionId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage, sources: [] }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage, session_id: sessionId })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          sources: data.sources || []
        }]);
      } else {
        // Show detailed error message
        let errorMessage = data.detail || 'An error occurred';
        
        // Check for specific error types
        if (errorMessage.toLowerCase().includes('billing') || 
            errorMessage.toLowerCase().includes('quota') ||
            errorMessage.toLowerCase().includes('exceeded')) {
          errorMessage = '⚠️ OpenAI API Billing Issue!\n\nYour API key has insufficient credits.\n\nPlease visit: https://platform.openai.com/account/billing\nAdd credits and try again.';
        } else if (errorMessage.toLowerCase().includes('invalid') && errorMessage.toLowerCase().includes('key')) {
          errorMessage = '❌ Invalid API Key!\n\nPlease check your OPENAI_API_KEY in backend/.env file.';
        } else if (errorMessage.toLowerCase().includes('rate')) {
          errorMessage = '⏳ Rate limit exceeded. Please wait a moment and try again.';
        }
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: errorMessage,
          sources: [],
          isError: true
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      let errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = '🔌 Cannot connect to the backend server.\n\nPlease make sure:\n1. MongoDB is running (mongod)\n2. Backend server is running on port 8000';
      }
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMessage,
        sources: [],
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
            <div className="w-24 h-24 mb-6 rounded-full bg-academic-teal/10 flex items-center justify-center">
              <BookOpen className="w-12 h-12 text-academic-teal" strokeWidth={1.5} />
            </div>
            <h2 className="font-heading text-3xl font-semibold mb-3">Welcome to Smart Campus Bot</h2>
            <p className="text-muted-foreground max-w-md">
              Upload your academic documents and ask questions. I'll help you find the information you need.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in`}
            >
              <div
                className={`max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-academic-teal text-white'
                    : 'bg-card border border-border'
                } p-4 shadow-sm`}
                data-testid={`chat-message-${message.role}`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/20 dark:border-border">
                    <p className="text-xs uppercase tracking-widest opacity-70 mb-2">Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {message.sources.map((source, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-1 text-xs font-mono bg-white/10 dark:bg-muted"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start animate-slide-in">
            <div className="bg-card border border-border p-4 shadow-sm">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-electric-indigo" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-border p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 glass rounded-full overflow-hidden">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 px-6"
              data-testid="chat-input"
              disabled={isLoading}
            />
          </div>
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !inputValue.trim()}
            data-testid="send-button"
            className="rounded-full"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
