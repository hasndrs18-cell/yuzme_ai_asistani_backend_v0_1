"use client";

import { CalendarDays, ChevronRight, Filter } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const demoNotice = "Henüz bağlı bir yarış kaydı yok. Yarışlar API üzerinden yetkili athlete scope ile yüklenecek.";

export default function RaceCalendarPage() {
  const [view, setView] = useState("LIST");
  const [priority, setPriority] = useState("ALL");
  return <main className="module-page race-page"><div className="detail-breadcrumb"><Link href="/swimbase">SWIMBASE</Link><ChevronRight size={13} /><span>RACE CALENDAR</span></div><header className="module-heading"><div><div className="eyebrow"><CalendarDays size={13} /> SWIMBASE / COMPETITION ENGINE</div><h1>RACE <em>CALENDAR</em></h1><p>Yarış tarihi, hedef zaman ve yalnızca ölçülmüş sonuçlarla hazırlık takibi.</p></div><div className="sync-badge"><i /> PERSISTED RACE DATA</div></header><div className="race-toolbar"><div className="category-tabs"><button type="button" className={view === "MONTH" ? "active" : ""} onClick={() => setView("MONTH")}>MONTH</button><button type="button" className={view === "WEEK" ? "active" : ""} onClick={() => setView("WEEK")}>WEEK</button><button type="button" className={view === "LIST" ? "active" : ""} onClick={() => setView("LIST")}>LIST</button></div><label><Filter size={13} /> PRIORITY <select value={priority} onChange={(event) => setPriority(event.target.value)}><option>ALL</option><option>A</option><option>B</option><option>C</option></select></label></div><section className="empty-race-state"><CalendarDays size={28} /><strong>{demoNotice}</strong><span>Race oluşturma ve result kayıtları `/api/v1/domain/races` endpoint’i üzerinden kalıcı PostgreSQL transaction’ı ile yapılır.</span></section></main>;
}
