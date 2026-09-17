"use client";

import { useEffect, useState } from "react";

export type AcademyContent = {
  id: string;
  content_type: string;
  title: string;
  slug: string;
  summary: string;
  body: string;
  language: string;
  level: string;
  category: string;
  status: string;
  source_id: string | null;
  source: { title: string; author: string | null; publication_year: number | null; publisher: string | null; journal: string | null; doi: string | null; url: string | null; source_type: string; evidence_level: string; last_checked: string | null } | null;
  lesson: { objective: string; estimated_duration_minutes: number | null; difficulty: string } | null;
};

export type AcademyLoadState = "loading" | "ready" | "empty" | "backend-unavailable" | "api-error" | "network-error";
type AcademyState = { data: AcademyContent[]; loading: boolean; error: string | null; status: AcademyLoadState; retry: () => void };

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export function useAcademyContent(query = "") {
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
  const [retryCount, setRetryCount] = useState(0);
  const [state, setState] = useState<AcademyState>({ data: [], loading: true, error: null, status: "loading", retry: () => setRetryCount((value) => value + 1) });
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    const params = new URLSearchParams({ language: "tr" });
    if (query.trim()) params.set("query", query.trim());
    fetch(`${backendUrl}/api/v1/academy?${params.toString()}`, { signal: controller.signal, cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP_${response.status}`);
        return response.json() as Promise<AcademyContent[]>;
      })
      .then((data) => setState({ data, loading: false, error: null, status: data.length ? "ready" : "empty", retry: () => setRetryCount((value) => value + 1) }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          setState({ data: [], loading: false, error: "Academy request timed out.", status: "network-error", retry: () => setRetryCount((value) => value + 1) });
          return;
        }
        const message = error instanceof Error ? error.message : "Academy content could not be loaded.";
        const status = message === "HTTP_503" ? "backend-unavailable" : message.startsWith("HTTP_") ? "api-error" : "network-error";
        setState({ data: [], loading: false, error: message, status, retry: () => setRetryCount((value) => value + 1) });
      });
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [query, retryCount]);
  return state;
}
