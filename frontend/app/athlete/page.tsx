import { ArrowRight, BookOpen, CircleUserRound, Dumbbell, ShieldCheck, Video } from "lucide-react";
import Link from "next/link";

const actions = [
  { title: "Academy", description: "Gerçek yayınlanmış içerikleri ve öğrenme yolunu aç.", href: "/academy", icon: BookOpen },
  { title: "Antrenman", description: "Günlük setlerini, CSS hedeflerini ve toparlanma verini takip et.", href: "/workouts", icon: Dumbbell },
  { title: "Video", description: "Yüzme videonu yükle, kareleri incele ve teknik geri bildirim al.", href: "/video-analysis", icon: Video },
];

export default function AthletePage() {
  return (
    <main className="module-page role-page">
      <header className="module-heading">
        <div><div className="eyebrow"><CircleUserRound size={14} /> SPORCU PANELİ</div><h1>BUGÜNÜN <em>AKIŞI</em></h1><p>Profilin, antrenmanın ve performans verilerin yalnızca yetkili hesabınla gösterilir.</p></div>
        <div className="sync-badge"><i /> GERÇEK VERİ BEKLENİYOR</div>
      </header>
      <section className="role-empty-state" aria-labelledby="athlete-state-title"><ShieldCheck size={22} /><div><h2 id="athlete-state-title">Sporcu verisi henüz bağlı değil</h2><p>Giriş yaptığında sana ait antrenman, performans, recovery ve hedef kayıtları burada görünür. Başka bir sporcunun verisi gösterilmez.</p><Link className="role-primary-link" href="/onboarding">Profil kurulumuna git <ArrowRight size={15} /></Link></div></section>
      <section className="role-action-grid" aria-label="Sporcu işlemleri">{actions.map(({ title, description, href, icon: Icon }) => <Link className="role-action-card" href={href} key={title}><Icon size={20} /><span><strong>{title}</strong><small>{description}</small></span><ArrowRight size={15} /></Link>)}</section>
    </main>
  );
}