import { ArrowRight, BarChart3, BookOpen, ClipboardList, ShieldCheck, UsersRound } from "lucide-react";
import Link from "next/link";

const actions = [
  { title: "Sporcular", description: "Yetkili takım ve sporcu kayıtları bağlandığında roster görünür.", href: "/swimbase/athletes", icon: UsersRound },
  { title: "Performans", description: "Yetkili sporcu performans verileri gerçek API’den yüklenecek.", href: "/swimbase/compare", icon: BarChart3 },
  { title: "Academy", description: "Antrenör eğitim içeriklerini ve yayınlanmış kaynakları aç.", href: "/academy", icon: BookOpen },
  { title: "Yarışlar", description: "Yetkili yarış kayıtlarını ve karşılaştırma akışını aç.", href: "/swimbase/races", icon: ClipboardList },
];

export default function CoachPage() {
  return (
    <main className="module-page role-page">
      <header className="module-heading">
        <div><div className="eyebrow"><UsersRound size={14} /> ANTRENÖR PANELİ</div><h1>TAKIMININ <em>DURUMU</em></h1><p>Takım, sporcu, antrenman ve performans bilgileri yalnızca yetkili organizasyon kapsamından yüklenir.</p></div>
        <div className="sync-badge"><i /> ORGANİZASYON BAĞLANTISI BEKLENİYOR</div>
      </header>
      <section className="role-empty-state" aria-labelledby="coach-state-title"><ShieldCheck size={22} /><div><h2 id="coach-state-title">İlk takımını oluştur</h2><p>Bu hesap için henüz yetkili takım veya sporcu kapsamı bulunmuyor. Sistem veri uydurmaz; organizasyon ve roster bağlandığında dashboard gerçek kayıtlarla dolar.</p><Link className="role-primary-link" href="/onboarding">Kuruluma git <ArrowRight size={15} /></Link></div></section>
      <section className="role-action-grid" aria-label="Antrenör işlemleri">{actions.map(({ title, description, href, icon: Icon }) => <Link className="role-action-card" href={href} key={title}><Icon size={20} /><span><strong>{title}</strong><small>{description}</small></span><ArrowRight size={15} /></Link>)}</section>
    </main>
  );
}