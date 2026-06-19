import React, { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2, Sparkles, FileText, Trash2, GraduationCap, AlertCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { fetchHistory, clearHistory, streamChat } from "../lib/api";

const SUGGESTIONS = [
  "Summarize the key points of my documents",
  "What are the important deadlines mentioned?",
  "Explain the admission requirements",
  "List the main topics covered",
];

export function ChatInterface({ sessionId, hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const endRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    (async () => {
      const history = await fetchHistory(sessionId);
      setMessages(
        history.map((m) => ({ role: m.role, content: m.content, sources: m.sources || [] }))
      );
    })();
  }, [sessionId]);

  const send = async (text) => {
    const query = (text ?? input).trim();
    if (!query || isStreaming) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: query, sources: [] },
      { role: "assistant", content: "", sources: [], pending: true },
    ]);
    setIsStreaming(true);

    const update = (fn) =>
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = fn(next[next.length - 1]);
        return next;
      });

    try {
      await streamChat({
        query,
        sessionId,
        onSources: (sources) => update((m) => ({ ...m, sources })),
        onToken: (token) =>
          update((m) => ({ ...m, content: m.content + token, pending: false })),
        onError: (message) =>
          update((m) => ({ ...m, content: message, isError: true, pending: false })),
        onDone: () => update((m) => ({ ...m, pending: false })),
      });
    } catch (e) {
      update((m) => ({
        ...m,
        content:
          "Cannot reach the server. Make sure the backend is running on port 8000.",
        isError: true,
        pending: false,
      }));
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    send();
  };

  const handleClear = async () => {
    try {
      await clearHistory(sessionId);
      setMessages([]);
      toast.success("Conversation cleared");
    } catch {
      toast.error("Failed to clear conversation");
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-6">
          {isEmpty ? (
            <EmptyState hasDocuments={hasDocuments} onPick={send} />
          ) : (
            <div className="space-y-5">
              {messages.map((m, i) => (
                <MessageBubble key={i} message={m} />
              ))}
            </div>
          )}
          <div ref={endRef} />
        </div>
      </div>

      {/* Composer */}
      <div className="shrink-0 border-t border-border/60 bg-background/60 backdrop-blur">
        <div className="mx-auto max-w-3xl px-4 py-3">
          {messages.length > 0 && (
            <div className="mb-2 flex justify-end">
              <button
                onClick={handleClear}
                className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Trash2 className="h-3.5 w-3.5" /> Clear conversation
              </button>
            </div>
          )}
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your documents…"
              disabled={isStreaming}
              className="h-12"
            />
            <Button type="submit" size="icon" className="h-12 w-12 shrink-0" disabled={isStreaming || !input.trim()}>
              {isStreaming ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </Button>
          </form>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            Answers are generated from your uploaded documents and may not always be complete.
          </p>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ hasDocuments, onPick }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-up">
      <div className="grid h-16 w-16 place-items-center rounded-2xl brand-gradient shadow-glow">
        <GraduationCap className="h-8 w-8 text-white" strokeWidth={1.8} />
      </div>
      <h2 className="mt-5 font-heading text-2xl font-semibold">Welcome to Smart Campus Bot</h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        {hasDocuments
          ? "Ask a question about your documents, or try one of these:"
          : "Upload a PDF or DOCX in the Documents tab, then start asking questions."}
      </p>

      {hasDocuments && (
        <div className="mt-6 grid w-full max-w-xl gap-2 sm:grid-cols-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => onPick(s)}
              className="group flex items-center gap-2.5 rounded-xl border border-border bg-card p-3 text-left text-sm transition-all hover:border-primary/40 hover:shadow-soft"
            >
              <Sparkles className="h-4 w-4 shrink-0 text-primary" />
              <span className="text-muted-foreground group-hover:text-foreground">{s}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 animate-fade-up ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${
          isUser ? "bg-muted" : "brand-gradient"
        }`}
      >
        {isUser ? (
          <span className="text-xs font-semibold text-muted-foreground">You</span>
        ) : (
          <GraduationCap className="h-4 w-4 text-white" />
        )}
      </div>

      <div className={`max-w-[82%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : message.isError
              ? "border border-red-500/30 bg-red-500/10 text-foreground rounded-tl-sm"
              : "card-surface rounded-tl-sm"
          }`}
        >
          {message.isError && (
            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-red-500">
              <AlertCircle className="h-3.5 w-3.5" /> Error
            </div>
          )}

          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : message.pending && !message.content ? (
            <div className="flex items-center gap-1.5 py-1">
              <span className="h-2 w-2 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-primary" />
            </div>
          ) : (
            <div className="prose-chat">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              {message.pending && <span className="cursor-blink">▋</span>}
            </div>
          )}
        </div>

        {message.sources?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.sources.map((src, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded-md bg-muted px-2 py-1 text-[11px] font-medium text-muted-foreground"
              >
                <FileText className="h-3 w-3" /> {src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
