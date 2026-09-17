import { ArrowLeft, CalendarDays, ChevronRight, ShieldCheck } from "lucide-react";
import Link from "next/link";

export default async function RaceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <main className="module-page race-detail-page"><div className="detail-breadcrumb"><Link href="/swimbase">SWIMBASE</Link><ChevronRight size={13} /><Link href="/swimbase/races">RACE CALENDAR</Link><ChevronRight size={13} /><span>{id}</span></div><header className="module-heading"><div><div className="eyebrow"><CalendarDays size={13} /> RACE DETAIL / PERSISTED RECORD</div><h1>RACE <em>DETAIL</em></h1><p>Bu ekran yalnızca yetkili API verisini gösterir; eksik split veya ölçüm uydurulmaz.</p></div><div className="sync-badge"><i /> ATHLETE SCOPE VERIFIED</div></header><section className="empty-race-state"><ShieldCheck size={28} /><strong>Yarış kaydı API’den yüklenmeye hazır.</strong><span>Race ID: {id}</span><Link href="/swimbase/races"><ArrowLeft size={14} /> TAKVİME DÖN</Link></section></main>;
}
