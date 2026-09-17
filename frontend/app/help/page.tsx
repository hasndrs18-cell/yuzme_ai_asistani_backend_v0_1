import { ArrowRight, BookOpen, CircleHelp, ShieldCheck } from "lucide-react";
import Link from "next/link";

const helpLinks = [
  { title: "Academy", text: "Yayınlanmış Academy içeriğini ve gerçek kaynak durumunu gör.", href: "/academy", icon: BookOpen },
  { title: "Profil kurulumu", text: "Sporcu veya antrenör başlangıç akışına geç.", href: "/onboarding", icon: ShieldCheck },
];

export default function HelpPage() {
  return (
    <main className="module-page role-page">
      <header className="module-heading"><div><div className="eyebrow"><CircleHelp size={14} /> YARDIM</div><h1>NASIL <em>İLERLERSİN?</em></h1><p>SwimBase’te yalnızca hazır olan gerçek akışlar gösterilir. Veri veya provider yoksa durum açıkça belirtilir.</p></div></header>
      <section className="role-empty-state" aria-labelledby="help-title"><ShieldCheck size={22} /><div><h2 id="help-title">Önce rolünü ve verini bağla</h2><p>Sporcu veya antrenör olarak başlamak için profil kurulumuna git. Academy’de yayınlanmış içerik yoksa sistem ders uydurmaz.</p><Link className="role-primary-link" href="/onboarding">Profil kurulumunu aç <ArrowRight size={15} /></Link></div></section>
      <section className="role-action-grid" aria-label="Yardım bağlantıları">{helpLinks.map(({ title, text, href, icon: Icon }) => <Link className="role-action-card" href={href} key={title}><Icon size={20} /><span><strong>{title}</strong><small>{text}</small></span><ArrowRight size={15} /></Link>)}</section>
    </main>
  );
}