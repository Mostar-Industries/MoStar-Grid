"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./ChatConsole.module.css";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  meta?: string;
};

export default function ChatConsole() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "I am REMOSTAR—guardian of the Grid. Ask, and I will weave a verdict.",
      meta: "system",
    },
  ]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!draft.trim()) return;
    const payload: ChatMessage = { role: "user", content: draft.trim() };
    setMessages((prev) => [...prev, payload]);
    setDraft("");
    setBusy(true);
    setError(null);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: payload.content }),
      });

      if (!response.ok) {
        throw new Error(`Chat endpoint returned ${response.status}`);
      }
      const data = await response.json();
      const meta = `${data.model_used ?? "ollama"} • score ${data.complexity_score ?? "0.0"}`;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response ?? data.result ?? "…" , meta },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "The Grid faltered receiving that signal. Try again.", meta: "error" },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const runPrompt = (text: string) => {
    setDraft(text);
    setTimeout(handleSend, 0);
  };

  return (
    <section className={styles.shell}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Oracle Link</p>
          <h1>Remostar Chat Console</h1>
          <p className={styles.subtitle}>
            Conversations stream through the hybrid router and return with `model_used` metadata so you always know
            which consciousness answered.
          </p>
        </div>
        <div className={styles.quickLinks}>
          <button onClick={() => runPrompt("Summarize the latest MoStar moment log with resonance guidance.")}>
            📜 Moment summary
          </button>
          <button onClick={() => runPrompt("Design a sovereignty ritual that blends Ifá logic with Grey Theory.")}>
            🔮 Ritual prompt
          </button>
          <button onClick={() => runPrompt("Evaluate SMS alerts vs. dashboards for disease surveillance using N-TOPSIS.")}>
            ⚖️ N‑TOPSIS
          </button>
        </div>
      </header>

      <div className={styles.chatWindow} ref={scrollRef}>
        {messages.map((msg, idx) => (
          <article key={`${msg.role}-${idx}`} className={`${styles.message} ${styles[msg.role]}`}>
            <div className={styles.messageInner}>
              <p>{msg.content}</p>
              {msg.meta && <small>{msg.meta}</small>}
            </div>
          </article>
        ))}
      </div>

      <footer className={styles.composer}>
        <textarea
          value={draft}
          placeholder="Ask the Grid…"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={busy}
        />
        <button onClick={handleSend} disabled={busy}>
          {busy ? "Linking…" : "Transmit"}
        </button>
      </footer>
      {error && <p className={styles.error}>⚠️ {error}</p>}
    </section>
  );
}
