import { useState, type KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface MessageInputProps {
  onSend: (content: string) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export function MessageInput({ 
  onSend, 
  isLoading, 
  placeholder = 'Napisz wiadomość...',
  disabled = false
}: MessageInputProps) {
  const [content, setContent] = useState('');

  const handleSend = async () => {
    if (!content.trim() || isLoading || disabled) return;
    
    await onSend(content.trim());
    setContent('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-2 items-end">
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? 'Konwersacja zakończona' : placeholder}
        disabled={isLoading || disabled}
        className="min-h-[60px] max-h-[120px] resize-none bg-white"
        rows={2}
      />
      <Button
        onClick={handleSend}
        disabled={!content.trim() || isLoading || disabled}
        className="h-[60px] px-4 bg-book-brown hover:bg-book-brown/90"
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </Button>
    </div>
  );
}
