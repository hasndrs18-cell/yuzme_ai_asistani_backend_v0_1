"use client";

import { Activity, Check, Clock3, Dumbbell, Gauge, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

const sessions = [
  { type: "ISINMA", title: "Teknik hazırlık", detail: "400 m rahat + 4 × 50 m drill", distance: "600 m", target: "RPE 3" },
  { type: "ANA SET", title: "CSS dayanıklılık", detail: "3 × 400 m / 30 sn dinlenme", distance: "1.200 m", target: "CSS + 5 sn" },
  { type: "AÇIK SU", title: "Açık Su Akıntı Navigasyon Seti", detail: "6 × 300 m / her 6 kulaçta yön kontrolü", distance: "1.800 m", target: "RPE 6" },
  { type: "AÇIK SU", title: "Pacing & Draft Antrenmanı", detail: "3 × (400 m tempo + 200 m draft ritmi)", distance: "1.800 m", target: "CSS + 8 sn" },
  { type: "AÇIK SU", title: "Boğaz Geçişi Dayanıklılık Seti", detail: "2 × 1.000 m değişken akıntı temposu", distance: "2.000 m", target: "Z2 / Z3" },
  { type: "SOĞUMA", title: "Aktif toparlanma", detail: "300 m karışık kolay", distance: "300 m", target: "RPE 2" },
];

export default function WorkoutsPage() {
  const [completed, setCompleted] = useState<number[]>([]);
  const [fourHundred, setFourHundred] = useState(330);
  const [twoHundred, setTwoHundred] = useState(150);
  const [heartRate, setHeartRate] = useState(148);
  const [lactate, setLactate] = useState(2.8);
  const css = useMemo(() => (fourHundred - twoHundred > 0 ? (fourHundred - twoHundred) / 2 : 0), [fourHundred, twoHundred]);
  const format = (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2, "0")}`;
  const toggle = (index: number) => setCompleted((current) => current.includes(index) ? current.filter((item) => item !== index) : [...current, index]);

  return <main className="module-page workouts-page">
    <header className="module-heading"><div><div className="eyebrow"><Dumbbell size={13} /> SWIMBASE / ANTRENMAN MOTORU</div><h1>BUGÜNÜN <em>ANTRENMANI</em></h1><p>Setlerini, hedef temposunu ve seans sonrası yükünü tek ekranda takip et. Verilerinin sahibi sensin; kaydetmeden hiçbir değer gönderilmez.</p></div><div className="sync-badge sync-live"><i /> 2.900 M · PLAN HAZIR</div></header>
    <div className="workout-layout">
      <section className="workout-schedule"><div className="section-title"><span><Clock3 size={14} /> BUGÜN / 17 EYLÜL</span><small>{completed.length}/{sessions.length} SET TAMAMLANDI</small></div>{sessions.map((session, index) => <article className={`workout-row ${completed.includes(index) ? "done" : ""}`} key={`${session.type}-${session.title}`}><button type="button" className="workout-check" onClick={() => toggle(index)} aria-label={`${session.title} tamamlandı olarak işaretle`}>{completed.includes(index) ? <Check size={15} /> : index + 1}</button><div><span>{session.type}</span><h2>{session.title}</h2><p>{session.detail}</p></div><div className="workout-metric"><strong>{session.distance}</strong><small>{session.target}</small></div></article>)}</section>
      <aside className="workout-side"><section className="metric-panel"><div className="section-title"><span><Gauge size={14} /> CSS TEMPO HESAPLAYICI</span></div><p>400 m ve 200 m test sürelerini saniye olarak gir.</p><label>400 M TEST<input type="number" min="1" value={fourHundred} onChange={(event) => setFourHundred(Number(event.target.value))} /></label><label>200 M TEST<input type="number" min="1" value={twoHundred} onChange={(event) => setTwoHundred(Number(event.target.value))} /></label><div className="css-result"><span>ÖNERİLEN CSS / 100 M</span><strong>{css ? format(css) : "--:--"}</strong></div></section>
      <section className="metric-panel"><div className="section-title"><span><Activity size={14} /> SEANS SONU KAYDI</span></div><p>Seans sonrası toparlanmanı izlemek için iki kısa değer gir.</p><label>ORT. NABIZ (BPM)<input type="number" min="0" value={heartRate} onChange={(event) => setHeartRate(Number(event.target.value))} /></label><label>LAKTAT (MMOL/L)<input type="number" min="0" step="0.1" value={lactate} onChange={(event) => setLactate(Number(event.target.value))} /></label><button type="button" className="primary-action" onClick={() => window.alert("Seans özeti bu cihazda hazırlandı.")}><Check size={15} /> SEANSI KAYDET</button></section></aside>
    </div>
    <button type="button" className="reset-workout" onClick={() => setCompleted([])}><RotateCcw size={13} /> İLERLEMEYİ SIFIRLA</button>
  </main>;
}
