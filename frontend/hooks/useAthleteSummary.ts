"use client";

import { useCallback, useEffect, useState } from "react";
import { AthleteSummary, emptySummaryState, fetchAthleteSummary } from "@/services/athleteSummary";

export function useAthleteSummary(athleteId: string) {
  const [state, setState] = useState<{ data: AthleteSummary | null; loading: boolean; error: string | null }>(emptySummaryState);
  const [retryKey, setRetryKey] = useState(0);
  const retry = useCallback(() => setRetryKey((key) => key + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    fetchAthleteSummary(athleteId, controller.signal).then((data) => setState({ data, loading: false, error: null })).catch((error: unknown) => { if (error instanceof DOMException && error.name === "AbortError") return; setState({ data: null, loading: false, error: error instanceof Error ? error.message : "Veriler yüklenemedi." }); });
    return () => controller.abort();
  }, [athleteId, retryKey]);
  return { ...state, retry };
}
