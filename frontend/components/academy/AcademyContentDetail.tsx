"use client";

import { ArrowLeft, CheckCircle2, RefreshCw, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { AcademyContent } from "@/hooks/useAcademyContent";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function AcademyContentDetail({ slug }: { slug: string }) {
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
  const [content, setContent] = useState<AcademyContent | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "not-found" | "backend-unavailable" | "api-error" | "network-error">("loading");
  const [progress, setProgress] = useState<{ status: string; progress_percent: number } | null>(null);
  const [progressState, setProgressState] = useState<"unavailable" | "ready" | "completed" | "error">("unavailable");
  const [retryCount, setRetryCount] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    fetch(`${backendUrl}/api/v1/academy/content/${encodeURIComponent(slug)}`, { signal: controller.signal, cache: "no-store" })
      .then(async (response) => {
        if (response.status === 404) { setState("not-found"); return null; }
        if (!response.ok) throw new Error(`HTTP_${response.status}`);
        return response.json() as Promise<AcademyContent>;
      })
      .then(async (data) => {
        if (!data) return;
        setContent(data); setState("ready");
        const token = window.localStorage.getItem("cyber-coach-access-token");
        if (!token) return;
        const progressResponse = await fetch(`${backendUrl}/api/v1/academy/progress`, { headers: { Authorization: `Bearer ${token}` }, signal: controller.signal, cache: "no-store" });
        if (!progressResponse.ok) { setProgressState("error"); return; }
        const rows = await progressResponse.json() as Array<{ content_id: string; status: string; progress_percent: number }>;
        const current = rows.find((row) => row.content_id === data.id) ?? null;
        setProgress(current); setProgressState(current?.status === "COMPLETED" ? "completed" : "ready");
      })
      .catch((error: unknown) => { if (error instanceof DOMException && error.name === "AbortError") { setState("network-error"); return; } const message = error instanceof Error ? error.message : ""; setState(message === "HTTP_503" ? "backend-unavailable" : message.startsWith("HTTP_") ? "api-error" : "network-error"); });
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, [slug, retryCount]);

  async function markComplete() {
    if (!content) return;
    const token = window.localStorage.getItem("cyber-coach-access-token");
    if (!token) { setProgressState("error"); return; }
    const response = await fetch(`${backendUrl}/api/v1/academy/progress/${content.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status: "COMPLETED", progress_percent: 100 }),
    });
    if (!response.ok) { setProgressState("error"); return; }
    setProgress(await response.json() as { status: string; progress_percent: number });
    setProgressState("completed");
  }

  if (state === "loading") return <main className="academy-detail-page"><p>Academy içeriği yükleniyor...</p></main>;
  if (state === "not-found") return <main className="academy-detail-page"><Link href="/academy"><ArrowLeft size={15} /> Academy’ye dön</Link><div className="academy-empty-state"><strong>İçerik bulunamadı.</strong><span>Bu slug ile yayınlanmış bir Academy içeriği yok.</span></div></main>;
  if (state !== "ready" || !content) return <main className="academy-detail-page"><Link href="/academy"><ArrowLeft size={15} /> Academy’ye dön</Link><div className="academy-empty-state"><strong>{state === "backend-unavailable" ? "Academy backend bağlantısı mevcut değil." : state === "api-error" ? "Academy içeriği yüklenemedi." : "Academy backend bağlantısı mevcut değil."}</strong><span>{state === "api-error" ? "Beklenmeyen bir API hatası oluştu." : "Gerçek içerik yüklenemedi; sahte içerik gösterilmiyor."}</span><button type="button" onClick={() => { setState("loading"); setRetryCount((value) => value + 1); }}><RefreshCw size={14} /> Tekrar Dene</button></div></main>;

  return <main className="academy-detail-page"><Link className="academy-back-link" href="/academy"><ArrowLeft size={15} /> ACADEMY’YE DÖN</Link><div className="academy-detail-kicker">{content.category} / {content.level}</div><h1>{content.title}</h1><p className="academy-detail-summary">{content.summary}</p><section className="academy-detail-content"><h2>BU DERSTE NE ÖĞRENECEKSİN?</h2><p>{content.body}</p>{content.lesson && <div className="academy-detail-practice"><strong>AMAÇ</strong><p>{content.lesson.objective}</p></div>}</section><section className="academy-provenance"><ShieldCheck size={16} /><div><strong>KAYNAK BİLGİSİ</strong>{content.source ? <><p>{content.source.title} · {content.source.source_type} · {content.source.evidence_level}</p>{content.source.author && <p>{content.source.author}{content.source.publication_year ? ` · ${content.source.publication_year}` : ""}</p>}{content.source.doi && <p>DOI: {content.source.doi}</p>}{content.source.last_checked && <p>Son kontrol: {content.source.last_checked}</p>}</> : <p>Kaynak henüz doğrulanmadı</p>}</div></section>{progressState === "ready" && progress && <p className="academy-provider-notice">İlerleme: %{progress.progress_percent}</p>}<button className="academy-complete-button" type="button" onClick={markComplete} disabled={progressState === "completed"}><CheckCircle2 size={16} /> {progressState === "completed" ? "TAMAMLANDI" : "TAMAMLANDI OLARAK İŞARETLE"}</button>{progressState === "error" && <p className="academy-provider-notice">İlerleme sağlayıcısı kullanılamıyor veya kimlik doğrulaması gerekli.</p>}</main>;
}
