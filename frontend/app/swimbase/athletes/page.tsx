import { ArrowLeft, UserRound } from "lucide-react";
import Link from "next/link";

const athletes = [
  { id: "demo-student", name: "Deneme Öğrencisi", lane: "KULVAR 04", status: "CANLI", focus: "Nefes zamanlaması", css: "1:32" },
  { id: "selin-kaya", name: "Selin Kaya", lane: "KULVAR 02", status: "HAZIR", focus: "Yüksek dirsek", css: "1:28" },
  { id: "mert-aydin", name: "Mert Aydın", lane: "KULVAR 06", status: "ARŞİV", focus: "Toparlanma ritmi", css: "1:36" },
];

export default function SwimBaseAthletesPage() {
  return <main className="module-page athlete-route-page"><div className="detail-breadcrumb"><Link href="/swimbase"><ArrowLeft size={13} /> SWIMBASE</Link><span>→ ATHLETE DATABASE</span></div><header className="module-heading"><div><div className="eyebrow"><UserRound size={13} /> SWIMBASE / ATHLETE MEMORY</div><h1>ATHLETE <em>DATABASE</em></h1><p>Sporcu profilleri, kulvar bilgisi ve performans hafızası.</p></div></header><div className="athlete-grid">{athletes.map((athlete) => <article className="athlete-card" key={athlete.id}><span className="student-avatar"><UserRound size={18} /></span><span><strong>{athlete.name}</strong><small>{athlete.lane} · {athlete.status}</small><em>{athlete.focus}</em></span><span className="athlete-metrics"><b>{athlete.css}</b><small>CSS / 100M</small></span></article>)}</div></main>;
}
