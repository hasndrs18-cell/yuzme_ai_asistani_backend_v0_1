"use client";

import { ArrowRight, BarChart3, BookOpen, CheckCircle2, Dumbbell, Droplets, HeartPulse, Search, ShieldCheck, Sparkles, Waves } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAcademyContent } from "@/hooks/useAcademyContent";
import { knowledgeArticles } from "@/components/knowledge/data";

type AcademyHomeProps = { onAskAstra?: (question: string) => void };

type AcademyCategory = {
  title: string;
  description: string;
  href?: string;
  icon: typeof Waves;
  status: "available" | "coming-soon";
};

const categories: AcademyCategory[] = [
  { title: "Swimming", description: "Strokes, starts, turns and underwater fundamentals.", href: "/knowledge/biomechanics", icon: Waves, status: "available" },
  { title: "Technique", description: "Body position, catch, timing and observable practice cues.", href: "/knowledge/biomechanics", icon: CheckCircle2, status: "available" },
  { title: "Drills", description: "Practice ideas that connect a drill to a full-stroke goal.", href: "/knowledge/training", icon: Dumbbell, status: "available" },
  { title: "Training", description: "Energy systems, sets, pacing and recovery principles.", href: "/knowledge/training", icon: BookOpen, status: "available" },
  { title: "Dryland", description: "Educational movement and strength foundations for swimmers.", href: "/knowledge/training/age-groups", icon: Dumbbell, status: "available" },
  { title: "Nutrition", description: "General fueling, hydration and food-first education.", href: "/knowledge/physiology/nutrition-hydration", icon: Droplets, status: "available" },
  { title: "Recovery", description: "Sleep, rest, load awareness and recovery literacy.", href: "/knowledge/physiology/recovery-physiology", icon: HeartPulse, status: "available" },
  { title: "Coaching", description: "Decision-making, observation and athlete communication.", href: "/knowledge/training/age-groups", icon: ShieldCheck, status: "available" },
];

export default function AcademyHome({ onAskAstra }: AcademyHomeProps) {
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const academy = useAcademyContent(submittedQuery);

  function submitQuestion(event: FormEvent) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;
    setSubmittedQuery(trimmedQuestion);
    const normalizedQuestion = trimmedQuestion.toLowerCase();
    const match = knowledgeArticles.find((article) => `${article.title} ${article.description} ${article.content}`.toLowerCase().includes(normalizedQuestion));
    if (match) router.push(`/knowledge/${match.category}/${match.slug}`);
    else router.push(`/knowledge?query=${encodeURIComponent(trimmedQuestion)}`);
    if (onAskAstra) onAskAstra(trimmedQuestion);
  }

  return (
    <main className="academy-page">
      <header className="academy-hero">
        <div className="academy-hero-copy">
          <div className="eyebrow"><BookOpen size={14} /> SWIMBASE / ÖĞRENME</div>
          <h1>SWIMBASE <em>ACADEMY</em></h1>
          <p>Yüzmeyi sadece yapmak değil, neden yaptığını anlamak için. Gerçek kaynaklarla öğren, antrenmanda uygula.</p>
        </div>
        <div className="academy-hero-mark"><Waves size={34} /><span>ÖĞREN · UYGULA · GELİŞ</span></div>
      </header>

      <section className="academy-question-band" aria-labelledby="academy-question-title">
        <div>
          <span className="section-kicker">SORU SOR</span>
          <h2 id="academy-question-title">Ne öğrenmek istiyorsun?</h2>
          <p>Yayınlanmış Academy içeriğinde ara. Astra sağlayıcısı bağlandığında kaynaklı soru-cevap akışı ayrıca kullanılabilir.</p>
        </div>
        <form className="academy-question-form" onSubmit={submitQuestion}>
          <Search size={18} />
          <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Örneğin: Serbestte daha hızlı nasıl olurum?" aria-label="Academy sorusu" />
          <button type="submit" disabled={!question.trim()}><Search size={16} /> ACADEMY&apos;DE ARA</button>
        </form>
      </section>

      <section className="academy-section" aria-labelledby="academy-tools-title">
        <div className="academy-section-heading"><div><span className="section-kicker">ANTRENMAN ARKADAŞIN</span><h2 id="academy-tools-title">SwimBase ile ne yapabilirsin?</h2></div></div>
        <div className="academy-feature-grid">
          <Link className="academy-feature-card aqua" href="/knowledge"><BookOpen size={20} /><span><strong>ÖĞREN</strong><small>Temelden ileri seviyeye gerçek Academy ve bilgi bankası içeriğini keşfet.</small></span><ArrowRight size={15} /></Link>
          <Link className="academy-feature-card blue" href="/video-analysis"><BarChart3 size={20} /><span><strong>ANALİZ ET</strong><small>Yüzme videonu incele ve teknik ölçüm hazırlığını başlat.</small></span><ArrowRight size={15} /></Link>
          <Link className="academy-feature-card green" href="/workouts"><Dumbbell size={20} /><span><strong>UYGULA</strong><small>Öğrendiğin tekniği günlük set ve tempo hedefleriyle uygula.</small></span><ArrowRight size={15} /></Link>
          <div className="academy-feature-card violet unavailable"><Sparkles size={20} /><span><strong>ASTRA&apos;YA SOR</strong><small>Provider yapılandırıldığında kaynaklı sorular burada yanıtlanır.</small><em>PROVIDER BAĞLI DEĞİL</em></span><ShieldCheck size={15} /></div>
        </div>
      </section>

      <section className="academy-section" aria-labelledby="continue-title">
        <div className="academy-section-heading"><div><span className="section-kicker">DEVAM ET</span><h2 id="continue-title">Kaldığın yerden devam et</h2></div><span className="academy-status">EĞİTİM İÇERİĞİ</span></div>
        {academy.loading && <div className="academy-empty-state">Academy içeriği yükleniyor...</div>}
        {!academy.loading && academy.status === "backend-unavailable" && <div className="academy-empty-state"><strong>Academy backend bağlantısı mevcut değil.</strong><span>Veritabanı bağlantısı kullanılamıyor.</span><button type="button" onClick={academy.retry}>Tekrar Dene</button></div>}
        {!academy.loading && academy.status === "api-error" && <div className="academy-empty-state"><strong>Academy içeriği yüklenemedi.</strong><span>Beklenmeyen bir API hatası oluştu.</span><button type="button" onClick={academy.retry}>Tekrar Dene</button></div>}
        {!academy.loading && academy.status === "network-error" && <div className="academy-empty-state"><strong>Academy backend bağlantısı mevcut değil.</strong><span>Ağ bağlantısını kontrol edip yeniden deneyin.</span><button type="button" onClick={academy.retry}>Tekrar Dene</button></div>}
        {!academy.loading && academy.status === "empty" && <div className="academy-empty-state">Henüz yayınlanmış bir öğrenme içeriği yok.</div>}
        {!academy.loading && academy.status === "ready" && academy.data[0]?.slug && <Link className="academy-continue-card" href={`/academy/content/${encodeURIComponent(academy.data[0].slug)}`}>
          <div><span className="academy-card-label">{academy.data[0].level} · {academy.data[0].category}</span><h3>{academy.data[0].title}</h3><p>{academy.data[0].summary}</p></div>
          <span className="academy-card-action">DERSİ AÇ <ArrowRight size={16} /></span>
        </Link>}
      </section>

      <section className="academy-section" aria-labelledby="explore-title">
        <div className="academy-section-heading"><div><span className="section-kicker">KEŞFET</span><h2 id="explore-title">Öğrenme alanları</h2></div><span className="academy-status">SAHTE İLERLEME YOK</span></div>
        <div className="academy-category-grid">
          {categories.map(({ title, description, href, icon: Icon, status }) => status === "available" && href ? (
            <Link className="academy-category-card" href={href} key={title}><Icon size={19} /><span><strong>{title}</strong><small>{description}</small></span><ArrowRight size={15} /></Link>
          ) : (
            <div className="academy-category-card unavailable" key={title}><Icon size={19} /><span><strong>{title}</strong><small>{description}</small><em>İÇERİK HATTI BAĞLI DEĞİL</em></span><ShieldCheck size={15} /></div>
          ))}
        </div>
      </section>

      <section className="academy-section" aria-labelledby="learning-path-title">
        <div className="academy-section-heading"><div><span className="section-kicker">ÖĞRENME YOLUN</span><h2 id="learning-path-title">Öğrenme yolun</h2></div><span className="academy-status">YALNIZCA GERÇEK İLERLEME</span></div>
        <div className="academy-empty-state academy-path-empty"><ShieldCheck size={18} /><div><strong>Henüz bir öğrenme yolu başlamadın.</strong><span>İçerik tamamlanma verisi oluştuğunda ilerlemen burada gösterilir.</span></div><Link href="/academy">ACADEMY&apos;Yİ KEŞFET <ArrowRight size={14} /></Link></div>
      </section>

      <footer className="academy-integrity-note"><ShieldCheck size={16} /><span>İçerik durumu ve kaynak doğrulaması görünür tutulur. Henüz gerçek progress, video lisansı veya uzman onayı olmayan alanlar başarı olarak gösterilmez.</span></footer>
    </main>
  );
}
