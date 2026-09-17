export type AthleteSummary = {
  athlete: { display_name: string; main_event?: string | null; dominant_stroke?: string | null; goals: string[] };
  readiness: { score: number; status: string; reasons: string[]; data_completeness: number; confidence: string } | null;
  recovery: { score: number | null; available_signals: string[]; missing_signals: string[] } | null;
  training_load: { daily: number | null; seven_day: number | null; twenty_eight_day: number | null; trend: string | null } | null;
  performance_trend: { count: number; trend: string; change_percent?: number } | null;
  active_plan: { plan_id: string; title?: string; goal: string; event: string; status: string } | null;
  next_race: { name: string; date: string; event: string; stroke: string; target_time?: number | null } | null;
  technical_development: Array<Record<string, unknown>> | null;
  generated_at: string;
};

type SummaryState = { data: AthleteSummary | null; loading: boolean; error: string | null };

export async function fetchAthleteSummary(athleteId: string, signal?: AbortSignal): Promise<AthleteSummary> {
  const token = window.localStorage.getItem("cyber-coach-access-token");
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
  const response = await fetch(`${backendUrl}/api/v1/domain/athletes/${encodeURIComponent(athleteId)}/summary`, { signal, headers: token ? { Authorization: `Bearer ${token}` } : undefined, cache: "no-store" });
  if (!response.ok) throw new Error(response.status === 401 ? "Oturum gerekli" : "Özet verileri yüklenemedi.");
  return response.json() as Promise<AthleteSummary>;
}

export function emptySummaryState(): SummaryState {
  return { data: null, loading: true, error: null };
}
