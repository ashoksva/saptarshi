"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { sendChat, type ChatResponse } from "@/lib/api";
import { RISHI_DOMAIN, RISHI_LABEL, RISHI_ORDER, type RishiId } from "@/lib/rishis";

type Phase = "idle" | "listening" | "thinking" | "speaking";

function getRecognition(): SpeechRecognition | null {
  if (typeof window === "undefined") return null;
  const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Ctor) return null;
  const recognition = new Ctor();
  recognition.lang = "en-IN";
  recognition.continuous = true;
  recognition.interimResults = true;
  return recognition;
}

function speak(text: string, onEnd: () => void) {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.96;
  utterance.onend = onEnd;
  utterance.onerror = onEnd;
  window.speechSynthesis.speak(utterance);
}

export function VoiceConsole() {
  const [supported, setSupported] = useState(true);
  const [phase, setPhase] = useState<Phase>("idle");
  const [live, setLive] = useState("");
  const [finalText, setFinalText] = useState("");
  const [typed, setTyped] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const transcriptRef = useRef("");
  const holdingRef = useRef(false);

  useEffect(() => {
    const recognition = getRecognition();
    setSupported(Boolean(recognition));
    recognitionRef.current = recognition;
    return () => {
      recognition?.abort();
      window.speechSynthesis.cancel();
    };
  }, []);

  const submit = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setError(null);
    setPhase("thinking");
    try {
      const data = await sendChat(trimmed);
      setResult(data);
      setPhase("speaking");
      speak(data.spoken, () => setPhase("idle"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setPhase("idle");
    }
  }, []);

  const stopListening = useCallback(() => {
    holdingRef.current = false;
    recognitionRef.current?.stop();
    const text = transcriptRef.current.trim();
    setLive("");
    if (text) {
      setFinalText(text);
      void submit(text);
    } else {
      setPhase("idle");
    }
  }, [submit]);

  const startListening = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setError("Voice needs Chrome or Edge with microphone permission.");
      return;
    }
    window.speechSynthesis.cancel();
    holdingRef.current = true;
    transcriptRef.current = "";
    setLive("");
    setFinalText("");
    setError(null);
    setPhase("listening");
    recognition.onresult = (event) => {
      let interim = "";
      let committed = "";
      for (let i = 0; i < event.results.length; i += 1) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) committed += `${piece} `;
        else interim += piece;
      }
      transcriptRef.current = (committed + interim).trim();
      setLive(transcriptRef.current);
    };
    recognition.onerror = (event) => {
      if (event.error !== "no-speech" && event.error !== "aborted") {
        setError(`Microphone: ${event.error}`);
      }
    };
    recognition.onend = () => {
      if (holdingRef.current) {
        try {
          recognition.start();
        } catch {
          /* already started */
        }
      }
    };
    try {
      recognition.start();
    } catch {
      /* already started */
    }
  }, []);

  const active = (result?.agents_used ?? []) as RishiId[];

  return (
    <div className="console">
      <header className="masthead">
        <p className="kicker">India · seven domains · supervisor</p>
        <h1>SAPTARSHI</h1>
        <p className="lede">
          Hold the star to speak. Questions about weather, grocery prices, banking,
          shopping, farming, insurance, or the Indian markets are routed to one rishi.
        </p>
      </header>

      <ol className="constellation" aria-label="Rishis">
        {RISHI_ORDER.map((id) => (
          <li
            key={id}
            className={active.includes(id) ? "star on" : "star"}
            data-rishi={id}
          >
            <span className="dot" />
            <span className="name">{RISHI_LABEL[id]}</span>
            <span className="lane">{RISHI_DOMAIN[id]}</span>
          </li>
        ))}
      </ol>

      <p className="phase" aria-live="polite">
        {phase === "idle" && "Ready"}
        {phase === "listening" && "Listening…"}
        {phase === "thinking" && "Supervisor routing…"}
        {phase === "speaking" && "Speaking…"}
      </p>

      <button
        type="button"
        className={phase === "listening" ? "talk holding" : "talk"}
        disabled={!supported || phase === "thinking"}
        onPointerDown={(event) => {
          event.preventDefault();
          (event.currentTarget as HTMLButtonElement).setPointerCapture(event.pointerId);
          startListening();
        }}
        onPointerUp={stopListening}
        onPointerCancel={stopListening}
      >
        <span className="talk-core" />
        Hold to talk
      </button>

      {!supported && (
        <p className="hint">
          This browser has no Web Speech API. Type below, or open Chrome / Edge.
        </p>
      )}

      <div className="transcript">
        <h2>Heard</h2>
        <p>{live || finalText || "—"}</p>
      </div>

      <form
        className="type-row"
        onSubmit={(event) => {
          event.preventDefault();
          const text = typed.trim();
          if (!text) return;
          setFinalText(text);
          setTyped("");
          void submit(text);
        }}
      >
        <input
          value={typed}
          onChange={(event) => setTyped(event.target.value)}
          placeholder="Or type a question"
          aria-label="Type a question"
        />
        <button type="submit" disabled={phase === "thinking"}>
          Send
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <article className="reply">
          <p className="route">
            {result.agents_display.join(" · ")} — {result.route_reason}
          </p>
          <p className="body">{result.reply}</p>
        </article>
      )}
    </div>
  );
}
