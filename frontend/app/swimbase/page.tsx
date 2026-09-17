import { ArrowRight, BarChart3, BookOpen, Dumbbell, Users } from "lucide-react";
import Link from "next/link";

const cards = [
  ["Knowledge Base", "Biyomekanik, fizyoloji ve antrenman rehberleri.", "/knowledge", BookOpen],
  ["Compare Athletes", "Sporcuları mesafe, pace, SPM, DPS ve CSS ile karşılaştır.", "/swimbase/compare", BarChart3],
  ["Training Library", "Set, drill ve yaş grubu metodolojisini incele.", "/knowledge/training", Dumbbell],
  ["Athlete Database", "Öğrenci profilleri ve performans hafızası.", "/swimbase/athletes", Users],
  ["Race Calendar", "Yarış takvimi, hedefler ve ölçülmüş sonuçlar.", "/swimbase/races", BarChart3],
] as const;

export default function SwimBasePage() {
  return <main className="module-page swimbase-page"><header className="module-heading"><div><div className="eyebrow"><BookOpen size={13} /> ASTRA-G7 / SWIMBASE</div><h1>SWIM <em>BASE</em></h1><p>Yüzme performansını keşfet, karşılaştır ve antrenman kararına dönüştür.</p></div><div className="sync-badge sync-live"><i /> PERFORMANCE OS ONLINE</div></header><div className="swimbase-grid">{cards.map(([title, description, href, Icon]) => <Link className="swimbase-card" href={href} key={title}><Icon size={22} /><h2>{title}</h2><p>{description}</p><span>OPEN MODULE <ArrowRight size={14} /></span></Link>)}</div></main>;
}
