export function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `${base.replace(/\/$/, "")}${path}`;
}

export type ChatResponse = {
  reply: string;
  spoken: string;
  agents_used: string[];
  agents_display: string[];
  route_reason: string;
  primary: string;
};

export async function sendChat(text: string): Promise<ChatResponse> {
  const response = await fetch(apiUrl("/v1/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Chat failed (${response.status})`);
  }
  return response.json() as Promise<ChatResponse>;
}
