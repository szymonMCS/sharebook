import { useEffect, useRef, useState } from 'react';
import { Send, Sparkles, Trash2, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { ChatMessage } from '@/components/ai/ChatMessage';
import { QuickSuggestions } from '@/components/ai/QuickSuggestions';
import { aiApi } from '@/api/ai';
import type { ChatMessage as ChatMessageType } from '@/types';

const QUICK_SUGGESTIONS = [
  'Poleć coś na smutek',
  'Thriller na wieczór',
  'Romans na walentynki',
  'Coś lekkiego na plażę',
  'Fantasy dla początkujących',
  'Klasyczna literatura',
];

export function AIChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, _setIsLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  

  

  // Start with welcome message
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Witaj! Jestem Twoim AI Bibliotekarzem. Pomogę Ci znaleźć idealną książkę. Napisz czego szukasz lub skorzystaj z sugestii poniżej!',
        recommendations: [],
        created_at: new Date().toISOString(),
      },
    ]);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (messageText: string = inputMessage) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiApi.chat(messageText);

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd komunikacji z AI');
      // Add error message
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Przepraszam, wystąpił błąd. Spróbuj ponownie za chwilę.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const handleClearHistory = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Witaj! Jestem Twoim AI Bibliotekarzem. Pomogę Ci znaleźć idealną książkę. Napisz czego szukasz lub skorzystaj z sugestii poniżej!',
        recommendations: [],
        created_at: new Date().toISOString(),
      },
    ]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />

      <main className="relative z-10 pt-16 lg:pt-20">
        <div className="max-w-4xl mx-auto px-4 py-6 lg:py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-serif font-bold text-book-brown">
                  AI Bibliotekarz
                </h1>
                <p className="text-sm text-book-muted">
                  Twój osobisty doradca literacki
                </p>
              </div>
            </div>
            {messages.length > 1 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearHistory}
                className="text-book-muted hover:text-red-600"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Wyczyść
              </Button>
            )}
          </div>

          

          {/* Chat Container */}
          <div className="bg-white rounded-2xl shadow-xl border border-stone-200/60 overflow-hidden">
            {/* Messages Area */}
            <div className="h-[60vh] lg:h-[65vh]">
              {isLoadingHistory ? (
                <div className="h-full flex items-center justify-center">
                  <div className="flex items-center gap-3 text-book-muted">
                    <Bot className="w-8 h-8 animate-pulse" />
                    <span>Ładowanie...</span>
                  </div>
                </div>
              ) : (
                <ScrollArea className="h-full p-4 lg:p-6">
                  <div className="space-y-6">
                    {messages.map((message) => (
                      <ChatMessage
                        key={message.id}
                        role={message.role}
                        content={message.content}
                        recommendations={message.recommendations}
                      />
                    ))}
                    {isLoading && (
                      <div className="flex items-center gap-3 text-book-muted pl-11">
                        <div className="flex gap-1">
                          <span
                            className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"
                            style={{ animationDelay: '0ms' }}
                          />
                          <span
                            className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"
                            style={{ animationDelay: '150ms' }}
                          />
                          <span
                            className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"
                            style={{ animationDelay: '300ms' }}
                          />
                        </div>
                        <span className="text-sm">AI pisze...</span>
                      </div>
                    )}
                    <div ref={scrollRef} />
                  </div>
                </ScrollArea>
              )}
            </div>

            {/* Input Area */}
            <div className="border-t border-stone-200 bg-stone-50 p-4 lg:p-6">
              {/* Quick Suggestions */}
              {!isLoading && messages.length <= 2 && (
                <QuickSuggestions
                  suggestions={QUICK_SUGGESTIONS}
                  onSuggestionClick={handleSuggestionClick}
                  className="mb-4"
                />
              )}

              {/* Input */}
              <div className="flex items-center gap-2">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    placeholder="Napisz czego szukasz..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                    className="pr-12 py-6 text-base bg-white border-stone-200 focus:border-book-gold focus:ring-book-gold/20"
                  />
                </div>
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-book-gold hover:bg-book-gold-hover text-white px-6 py-6"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>

              {/* Error */}
              {error && (
                <p className="text-red-600 text-sm mt-2">{error}</p>
              )}

              {/* Hint */}
              <p className="text-xs text-book-muted mt-3 text-center">
                AI Bibliotekarz pomoże Ci znaleźć idealną książkę. Twoje rozmowy są prywatne.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
