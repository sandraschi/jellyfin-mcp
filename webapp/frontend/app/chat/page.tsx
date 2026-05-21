'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  MessageSquare,
  Send,
  User,
  Bot,
  Loader2,
  Sparkles,
  Trash2,
} from 'lucide-react';
import { fetchChatHistory, sendChatMessage } from '@/utils/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

const MODELS = [
  { id: 'gpt-4o', label: 'GPT-4o', provider: 'OpenAI' },
  { id: 'claude-opus-4', label: 'Claude Opus 4', provider: 'Anthropic' },
  { id: 'llama3', label: 'Llama 3', provider: 'Local' },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [model, setModel] = useState(MODELS[0].id);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      const data = await fetchChatHistory();
      setMessages((data as Message[]) || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load chat history');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setSending(true);
    setError(null);

    try {
      const data = await sendChatMessage(input, model);
      const reply = (data as any).response || (data as any).content || 'No response';
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-0 overflow-hidden">
      <div className="flex items-center justify-between pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">AI Chat</h2>
          <p className="mt-1 text-sm text-[#777790]">Ask about your media library</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="rounded-lg border border-[#ffffff10] bg-jellyfin-surface px-3 py-2 text-xs text-white"
          >
            {MODELS.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setMessages([])}
            className="btn-secondary inline-flex items-center gap-1.5 text-xs"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto pr-2">
        {loading ? (
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-jellyfin-purple" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-jellyfin-purple/20 to-jellyfin-blue/20">
              <Sparkles className="h-8 w-8 text-jellyfin-purple" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-white">Jellyfin++ AI Assistant</h3>
            <p className="mt-2 max-w-md text-sm text-[#666680]">
              Ask me anything about your media library. I can help you find movies, suggest
              content, manage playback, and more.
            </p>
            <div className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {[
                'What horror movies do I have?',
                'Suggest something like Interstellar',
                'What\'s currently playing?',
                'Show me recently added movies',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => { setInput(suggestion); }}
                  className="rounded-lg border border-[#ffffff10] bg-jellyfin-surface px-4 py-2.5 text-left text-xs text-[#999] transition-colors hover:border-jellyfin-purple/30 hover:text-white"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4 pb-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-jellyfin-purple to-jellyfin-blue">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === 'user'
                      ? 'rounded-br-md bg-gradient-to-r from-jellyfin-purple to-jellyfin-purple-dark text-white'
                      : 'rounded-bl-md bg-jellyfin-surface border border-[#ffffff06] text-white'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.role === 'user' && (
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-jellyfin-surface-light">
                    <User className="h-4 w-4 text-jellyfin-purple" />
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="flex justify-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-jellyfin-purple to-jellyfin-blue">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="rounded-2xl rounded-bl-md border border-[#ffffff06] bg-jellyfin-surface px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-jellyfin-purple [animation-delay:-0.3s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-jellyfin-purple [animation-delay:-0.15s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-jellyfin-purple" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="border-t border-[#ffffff08] pt-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            className="input-field flex-1"
            disabled={sending}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="btn-primary inline-flex items-center gap-2 rounded-xl px-5"
          >
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
