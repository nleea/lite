"use client";

import { useState } from "react";

import { Button } from "@/components/atoms/Button";
import { Card } from "@/components/atoms/Card";
import { Input } from "@/components/atoms/Input";
import { ai } from "@/lib/api";
import type { ChatResponse } from "@/types";

interface Turn {
  question: string;
  answer: string;
  sources: string[];
  tools: string[];
}

export function AgentChat() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await ai.post<ChatResponse>("/agent/chat", { question });
      setTurns((t) => [
        ...t,
        {
          question,
          answer: res.answer,
          sources: res.sources.map((s) => s.code),
          tools: res.tools_used ?? [],
        },
      ]);
      setQuestion("");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <p className="mb-4 text-sm text-slate-500">
        Ask about the catalogue. The agent can search products, list companies,
        summarize inventory, and email the inventory PDF — e.g. &quot;email the
        inventory to me@x.com&quot; or &quot;how many products does OutdoorCo have?&quot;.
      </p>
      <div className="mb-4 space-y-4">
        {turns.map((t, i) => (
          <div key={i}>
            <p className="font-medium text-slate-800">You: {t.question}</p>
            <p className="mt-1 whitespace-pre-wrap text-slate-700">{t.answer}</p>
            {t.tools.length > 0 && (
              <div className="mt-1 flex flex-wrap gap-1">
                {t.tools.map((tool, j) => (
                  <span
                    key={j}
                    className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500"
                  >
                    🛠 {tool}
                  </span>
                ))}
              </div>
            )}
            {t.sources.length > 0 && (
              <p className="mt-1 text-xs text-slate-400">Sources: {t.sources.join(", ")}</p>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={ask} className="flex gap-2">
        <Input
          placeholder="e.g. waterproof products under 100 USD"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <Button type="submit" disabled={loading}>
          {loading ? "…" : "Ask"}
        </Button>
      </form>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </Card>
  );
}
