import { ArrowRight, Compass, PlayCircle, Waves } from "lucide-react";
import Link from "next/link";

export default function SwimbaseHero() {
  return <section className="swimbase-hero" aria-labelledby="hero-title">
    <div className="hero-media" role="img" aria-label="Açık suda yüzen sporcu"></div>
    <div className="hero-shade" />
    <div className="hero-content"><span className="hero-kicker"><Waves size={14} /> YÜZME PERFORMANSINI ANLA · UYGULA · GELİŞTİR</span><h1 id="hero-title">Suyun içindeki kararlarını <em>veriye dönüştür.</em></h1><p>SwimBase; sporcu, antrenör ve yüzme topluluklarını teknik öğrenme, günlük antrenman ve açık su deneyimi etrafında buluşturan kişisel performans çalışma alanıdır.</p><div className="hero-actions"><Link className="hero-primary" href="/athlete">BUGÜNÜN AKIŞINI AÇ <ArrowRight size={15} /></Link><Link className="hero-secondary" href="/academy"><PlayCircle size={16} /> ÖĞRENME YOLUNU KEŞFET</Link></div></div>
    <div className="hero-facts"><span><b>01</b><small>TEKNİK</small><strong>Video ve biomekanik</strong></span><span><b>02</b><small>PLAN</small><strong>CSS odaklı antrenman</strong></span><span><b>03</b><small>TOPLULUK</small><strong>Gerçek deneyimler</strong></span></div>
    <div className="hero-compass"><Compass size={17} /><span>AÇIK SU HAZIRLIK MODU</span></div>
  </section>;
}
