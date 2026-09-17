"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Activity, ArrowUp, BrainCircuit, CalendarDays, CheckCircle2, ChevronRight, CircleAlert, Gauge, HeartPulse, MessageCircle, ScanLine, UserRound, Waves } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { useI18n } from "@/app/i18n";
import type { StudentProfile } from "@/components/profiles/StudentProfilesPanel";
import { useAthleteSummary } from "@/hooks/useAthleteSummary";

type EventPayload = { type?: string; text?: string; code?: string; message?: string; [key: string]: unknown };
type ChatItem = { id: number; kind: "user" | "assistant" | "system" | "tool"; label: string; text: string };
type RobotSignal = { alert: boolean; focus: "shoulder" | "wrist" | "hip" | "knee" };
type CyberCoachPanelProps = { heartRate: number; cssPaceSeconds: number; timeline: number; onTimelineChange: (timeline: number) => void; selectedStudent: StudentProfile; onRobotSignal: (signal: RobotSignal) => void; onTelemetryChange: (heartRate: number, cssPaceSeconds: number) => void; knowledgePrompt?: string };

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
const configuredWebSocketUrl = process.env.NEXT_PUBLIC_WS_URL;

function socketUrl() {
  if (configuredWebSocketUrl) return configuredWebSocketUrl;
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
  const url = new URL(backendUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws/chat";
  return url.toString();
}

export default function CyberCoachPanel({ heartRate, cssPaceSeconds, timeline, onTimelineChange, selectedStudent, onRobotSignal, onTelemetryChange, knowledgePrompt }: CyberCoachPanelProps) {
  const { locale, t } = useI18n();
  const [connected, setConnected] = useState(false);
  const [message, setMessage] = useState("");
  const [token, setToken] = useState(() => typeof window === "undefined" ? "" : window.localStorage.getItem("cyber-coach-access-token") ?? "");
  const [coachMode, setCoachMode] = useState<"coach" | "athlete">("athlete");
  const [activeDrawer, setActiveDrawer] = useState<"readiness" | "workout" | "performance" | "recovery" | "race" | null>(null);
  const [items, setItems] = useState<ChatItem[]>([
    { id: 1, kind: "system", label: "ASTRA", text: "Astra hazır. Persisted athlete context ve backend tool bağlantısı gerektiğinde yanıt üretir." },
  ]);
  const summary = useAthleteSummary(selectedStudent.id);
  const socket = useRef<WebSocket | null>(null);
  const nextId = useRef(2);
  const reconnectAttempt = useRef(0);
  const reconnectTimer = useRef<number | null>(null);
  const allowReconnect = useRef(true);

  function addItem(item: Omit<ChatItem, "id">) {
    setItems((current) => [...current, { ...item, id: nextId.current++ }]);
  }

  function connect() {
    if (socket.current?.readyState === WebSocket.OPEN) return;
    const url = new URL(socketUrl());
    url.searchParams.set("student_id", selectedStudent.id);
    if (token.trim()) url.searchParams.set("access_token", token.trim());
    const nextSocket = new WebSocket(url);
    socket.current = nextSocket;
    nextSocket.onopen = () => { reconnectAttempt.current = 0; setConnected(true); addItem({ kind: "system", label: "LINK", text: locale === "tr" ? "WebSocket bağlantısı kuruldu." : "WebSocket link established." }); };
    nextSocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as EventPayload;
        if (typeof payload.heart_rate === "number" && typeof payload.css_pace_seconds_per_100m === "number") onTelemetryChange(payload.heart_rate, payload.css_pace_seconds_per_100m);
        if (payload.type === "assistant.text") addItem({ kind: "assistant", label: "COACH", text: payload.text ?? "" });
        else if (payload.type === "error") addItem({ kind: "tool", label: payload.code ?? "ERROR", text: payload.message ?? "İstek işlenemedi." });
        else if (payload.type === "assistant.thinking") addItem({ kind: "system", label: "ANALİZ", text: "Astra gerçek araç sonuçlarını değerlendiriyor..." });
        else if (payload.type === "session.ready") addItem({ kind: "system", label: "SESSION", text: `Oturum aktif: ${String(payload.session_id).slice(0, 12)}` });
        else if (payload.type === "tool.result" || payload.type === "css.result" || payload.type === "workout.result") addItem({ kind: "tool", label: t.toolOutput, text: JSON.stringify(payload, null, 2) });
        else if (payload.type !== "assistant.done") addItem({ kind: "system", label: payload.type ?? "EVENT", text: JSON.stringify(payload) });
      } catch { addItem({ kind: "system", label: "RAW", text: event.data }); }
    };
    nextSocket.onclose = () => {
      setConnected(false);
      addItem({ kind: "tool", label: "ASTRA", text: "Astra bağlantısı koptu. Yeniden bağlanılıyor..." });
      if (!allowReconnect.current || !token.trim()) return;
      const delay = Math.min(15000, 1000 * 2 ** reconnectAttempt.current);
      reconnectAttempt.current += 1;
      reconnectTimer.current = window.setTimeout(connect, delay);
    };
    nextSocket.onerror = () => addItem({ kind: "tool", label: "ASTRA", text: "Astra sağlayıcısı veya backend bağlantısı yapılandırılmamış." });
  }

  useEffect(() => () => {
    allowReconnect.current = false;
    if (reconnectTimer.current !== null) window.clearTimeout(reconnectTimer.current);
    socket.current?.close();
  }, []);

  useEffect(() => {
    if (!knowledgePrompt) return;
    const timer = window.setTimeout(() => {
      setMessage(knowledgePrompt);
      addItem({ kind: "system", label: "KNOWLEDGE CONTEXT", text: "Konu bağlamı composer'a yüklendi. Astra-G7'ye göndermek için mesajı düzenleyebilir veya doğrudan iletebilirsin." });
    }, 0);
    return () => window.clearTimeout(timer);
  }, [knowledgePrompt]);

  useEffect(() => {
    if (!token.trim() || connected) return;
    const timer = window.setTimeout(connect, 0);
    return () => window.clearTimeout(timer);
  // connect closes over the current session and token values.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected, token]);

  function send(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || socket.current?.readyState !== WebSocket.OPEN) return;
    socket.current.send(JSON.stringify({ type: "message.send", text, knowledge_base: "Master Swimming Knowledge Engine / World Aquatics sync: today" }));
    addItem({ kind: "user", label: "YOU", text });
    setMessage("");
  }

  function runAction(action: string) {
    const prompt = `${action}. Seçili sporcu: ${selectedStudent.name}. ${coachMode === "coach" ? "Antrenör seviyesinde, veri/provenance ayrımıyla yanıtla." : "Sporcu seviyesinde sade ve uygulanabilir anlat."}`;
    if (socket.current?.readyState !== WebSocket.OPEN) {
      addItem({ kind: "tool", label: "ASTRA", text: "Bu aksiyon için Astra bağlantısı açık değil. Gerçek sonuç üretmek için authentication ve backend bağlantısı gerekir." });
      return;
    }
    socket.current.send(JSON.stringify({ type: "message.send", text: prompt, knowledge_base: "Master Swimming Knowledge Engine / World Aquatics sync: today" }));
    addItem({ kind: "user", label: "ACTION", text: action });
  }

  const quickActions = ["BUGÜNÜ ANALİZ ET", "ANTRENMAN OLUŞTUR", "PERFORMANSI ANALİZ ET", "TEKNİĞİ GELİŞTİR", "YARIŞA HAZIRLAN", "RECOVERY ANALİZİ"];

  const statusValue = summary.loading ? "Yükleniyor" : summary.error ? "Dikkat gerekiyor" : summary.data ? "Hazır" : "Veri bekleniyor";
  const readinessValue = summary.data?.readiness ? `${summary.data.readiness.score} / 100` : "Veri yok";
  const loadValue = summary.data?.training_load?.seven_day != null ? `${summary.data.training_load.seven_day} AU` : "Veri yok";
  const recoveryValue = summary.data?.recovery?.score != null ? `${summary.data.recovery.score} / 100` : "Veri yok";
  const performanceValue = summary.data?.performance_trend?.change_percent != null ? `${summary.data.performance_trend.change_percent > 0 ? "+" : ""}${summary.data.performance_trend.change_percent}%` : "Veri yok";
  const metricCards = [
    { label: "READINESS", value: readinessValue, note: summary.data?.readiness?.status ?? "Wellness verisi bekleniyor", icon: HeartPulse, panel: "readiness" as const },
    { label: "TRAINING LOAD", value: loadValue, note: summary.data?.training_load?.trend ?? "Yük kaydı bulunmuyor", icon: Gauge, panel: "workout" as const },
    { label: "RECOVERY", value: recoveryValue, note: summary.data?.recovery ? `${summary.data.recovery.available_signals.length} sinyal mevcut` : "Recovery sinyali bekleniyor", icon: Activity, panel: "recovery" as const },
    { label: "PERFORMANCE", value: performanceValue, note: summary.data?.performance_trend?.trend ?? "Timeline için kayıt gerekli", icon: TrendingUpIcon, panel: "performance" as const },
  ];
  return <section className="coach-panel astra-console">
    <header className="astra-console-header"><div><div className="eyebrow"><Waves size={13} /> AQUA INTELLIGENCE / 04</div><h2>ASTRA ANTRENÖR KONSOLU</h2><p>Bugünkü performansını, toparlanmanı ve antrenmanını tek yerden yönet.</p></div><span className={`console-status ${connected ? "ready" : "waiting"}`}><i /> {statusValue}</span></header>
    <div className="athlete-context-bar"><span><UserRound size={14} /> SPORCU</span><strong>{summary.data?.athlete.display_name ?? selectedStudent.name}</strong><small>{summary.data?.athlete.main_event ?? selectedStudent.lane} · {summary.data?.athlete.dominant_stroke ?? selectedStudent.focus}</small><em>{summary.data?.generated_at ? `Son veri: ${new Date(summary.data.generated_at).toLocaleString(locale === "tr" ? "tr-TR" : "en-US")}` : "Henüz güncel veri yok."}</em></div>
    <section className="athlete-status-section"><div className="section-title"><span>BUGÜNKÜ DURUM</span><small>DATA / CALCULATION</small></div><div className="status-card-grid">{metricCards.map(({ label, value, note, icon: Icon, panel }) => <button type="button" className="status-card" key={label} onClick={() => setActiveDrawer(panel)}><Icon size={16} /><span>{label}</span><strong>{value}</strong><small>{note}</small><ChevronRight size={14} /></button>)}</div></section>
    <section className="today-workout-card"><div className="section-title"><span><CalendarDays size={14} /> BUGÜNKÜ ANTRENMAN</span><small>{summary.data?.active_plan ? summary.data.active_plan.status : "PLAN"}</small></div><div className="empty-console-state"><CheckCircle2 size={18} /><strong>{summary.data?.active_plan ? `Aktif plan: ${summary.data.active_plan.goal}` : "Bugün için aktif antrenman planı yok."}</strong><span>{summary.data?.active_plan ? "Bugünkü workout assignment endpoint’i bağlandığında set detayları burada gösterilecek." : "Plan oluşturmak için Astra aksiyonlarından birini seç veya koç onaylı bir planı bağla."}</span></div><div className="console-actions"><button type="button" onClick={() => runAction("ANTRENMAN OLUŞTUR")}>ANTRENMAN OLUŞTUR</button><button type="button" onClick={() => setActiveDrawer("workout")}>DETAYLARI GÖR</button></div></section>
    <section className="astra-actions-section"><div className="section-title"><span><BrainCircuit size={14} /> ASTRA AKSİYONLARI</span><div className="coach-mode-toggle"><button type="button" className={coachMode === "athlete" ? "active" : ""} onClick={() => setCoachMode("athlete")}>SPORCU</button><button type="button" className={coachMode === "coach" ? "active" : ""} onClick={() => setCoachMode("coach")}>ANTRENÖR</button></div></div><div className="quick-action-grid">{quickActions.map((action) => <button type="button" key={action} onClick={() => runAction(action)}>{action}</button>)}</div></section>
    <section className="technical-development"><div className="section-title"><span><ScanLine size={14} /> TEKNİK GELİŞİM</span><small>OBSERVATION</small></div><div className="empty-console-state compact"><CircleAlert size={17} /><strong>Henüz teknik gözlem bulunmuyor.</strong><span>Video analiz motoru yapılandırılmadan biomekanik hata iddia edilmez.</span></div></section>
    <section className="session-console"><div className="section-title"><span><Gauge size={14} /> ANTRENMAN SEANSI</span><small>MANUEL TAKİP</small></div><div className="session-unavailable"><span>Canlı cihaz verisi bağlı değil.</span><small>Manuel session tracking backend’e henüz bağlanmadı.</small></div></section>
    <div className="astra-chat-stream"><AnimatePresence initial={false}>{items.map((item) => <motion.article key={item.id} className={`chat-card ${item.kind}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}><div className="chat-card-label">{item.kind === "assistant" ? <BrainCircuit size={13} /> : item.kind === "tool" ? <CircleAlert size={13} /> : null}{item.label}</div><p>{item.text}</p></motion.article>)}</AnimatePresence></div>
    <form className="composer" onSubmit={send}><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder={connected ? "Astra'ya gerçek verilerin hakkında sor..." : "Astra sağlayıcısı yapılandırılmamış veya bağlantı bekliyor..."} maxLength={4000} /><button type="submit" disabled={!connected || !message.trim()} aria-label={t.send}><ArrowUp size={18} /></button></form>
    {summary.error && <div className="summary-error"><span>{summary.error}</span><button type="button" onClick={summary.retry}>TEKRAR DENE</button></div>}
    {activeDrawer && <div className="console-drawer" role="dialog" aria-modal="true"><button type="button" className="drawer-dismiss" onClick={() => setActiveDrawer(null)} aria-label="Kapat">×</button><div className="eyebrow">ASTRA / {activeDrawer.toUpperCase()}</div><h3>{activeDrawer === "readiness" ? "Readiness Analizi" : activeDrawer === "performance" ? "Performans Analizi" : activeDrawer === "recovery" ? "Recovery Analizi" : "Bugünkü Antrenman"}</h3>{activeDrawer === "readiness" && summary.data?.readiness ? <div className="drawer-facts"><strong>{summary.data.readiness.score} / 100</strong><span>{summary.data.readiness.status}</span><small>Güven: {summary.data.readiness.confidence} · Veri bütünlüğü: {Math.round(summary.data.readiness.data_completeness * 100)}%</small><p>{summary.data.readiness.reasons.join(" · ")}</p></div> : activeDrawer === "performance" && summary.data?.performance_trend ? <div className="drawer-facts"><strong>{summary.data.performance_trend.trend}</strong><span>{summary.data.performance_trend.count} kayıt</span><p>Değişim: {summary.data.performance_trend.change_percent ?? "Veri yok"}%</p></div> : <div className="drawer-empty"><MessageCircle size={16} /> Veri yok. İlgili ölçüm veya plan kaydı eklendiğinde burada açıklanabilir sonuç gösterilecek.</div>}</div>}
  </section>;
}

function TrendingUpIcon({ size }: { size?: number }) { return <Activity size={size} />; }