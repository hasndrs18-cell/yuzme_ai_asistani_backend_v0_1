"use client";

import { ArrowLeft, BrainCircuit, Calculator, ChevronRight, Clock3, Dumbbell, Gauge, MessageCircle, Target } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { getArticle, KnowledgeArticle } from "./data";

type KnowledgeDetailProps = { article: KnowledgeArticle };

function AstraPanel({ article }: { article: KnowledgeArticle }) {
  const [mode, setMode] = useState<"coach" | "athlete">("coach");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  function ask(prompt = question) {
    if (!prompt.trim()) return;
    setQuestion(prompt);
    setAnswer(mode === "coach"
      ? `Astra-G7 / Antrenör modu: ${article.title} için önce ${article.metrics.join(", ")} verilerini aynı sette izleyin. ${article.coachSummary}`
      : `Astra-G7 / Sporcu modu: ${article.athleteSummary} Bugünkü çalışmanda hareketi yavaş ve temiz yap, sonra kısa tekrarlarla hızı artır.`);
  }

  return <aside className="astra-detail-panel"><div className="astra-panel-heading"><span><BrainCircuit size={15} /> ASTRA-G7 BAĞLAMI</span><i /></div><div className="assistant-modes"><button type="button" className={mode === "coach" ? "active" : ""} onClick={() => setMode("coach")}>ANTRENÖR</button><button type="button" className={mode === "athlete" ? "active" : ""} onClick={() => setMode("athlete")}>SPORCU</button></div><p className="astra-context">Şu anda <strong>{article.title}</strong> inceleniyor. Sorular makale bağlamı, kategori ve metriklerle birlikte yanıtlanır.</p><div className="quick-prompts">{article.quickPrompts.map((prompt) => <button type="button" key={prompt} onClick={() => ask(prompt)}>{prompt}</button>)}</div><div className="detail-composer"><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Bu konu hakkında Astra-G7'ye sor..." /><button type="button" onClick={() => ask()} aria-label="Astra'ya sor"><MessageCircle size={16} /></button></div>{answer && <div className="astra-answer"><span>ASTRA-G7</span><p>{answer}</p></div>}</aside>;
}

function CssCalculator() {
  const [fourHundred, setFourHundred] = useState(300);
  const [twoHundred, setTwoHundred] = useState(140);
  const result = useMemo(() => { const speed = (400 - 200) / Math.max(1, fourHundred - twoHundred); const pace100 = 100 / speed; return { pace100, pace50: pace100 / 2, en1: pace100 + 8, en2: pace100 + 2, en3: pace100 - 3 }; }, [fourHundred, twoHundred]);
  const format = (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2, "0")}`;
  return <div className="css-calculator"><div className="calculator-heading"><Calculator size={16} /><span>CSS TEMPO HESAPLAYICI</span></div><div className="calculator-inputs"><label>400 M SÜRE (SANİYE)<input type="number" min="1" value={fourHundred} onChange={(event) => setFourHundred(Number(event.target.value))} /></label><label>200 M SÜRE (SANİYE)<input type="number" min="1" value={twoHundred} onChange={(event) => setTwoHundred(Number(event.target.value))} /></label></div><div className="calculator-results"><div><span>CSS / 100 M</span><strong>{format(result.pace100)}</strong></div><div><span>CSS / 50 M</span><strong>{format(result.pace50)}</strong></div><div><span>EN1</span><strong>{format(result.en1)}</strong></div><div><span>EN2</span><strong>{format(result.en2)}</strong></div><div><span>EN3</span><strong>{format(result.en3)}</strong></div></div></div>;
}

export default function KnowledgeDetail({ article }: KnowledgeDetailProps) {
  const related = article.relatedArticles.map((slug) => getArticle(slug)).filter((item): item is KnowledgeArticle => Boolean(item));
  return <main className="knowledge-detail-page"><div className="detail-breadcrumb"><Link href="/swimbase">SwimBase</Link><ChevronRight size={13} /><Link href="/knowledge">Yüzme Bilgi Bankası</Link><ChevronRight size={13} /><Link href={`/knowledge/${article.category}`}>{article.categoryLabel}</Link><ChevronRight size={13} /><span>{article.title}</span></div><div className="detail-layout"><article className="article-reading"><Link className="back-link" href="/knowledge"><ArrowLeft size={14} /> BİLGİ BANKASINA DÖN</Link><div className="detail-kicker">{article.categoryLabel} / {article.difficulty}</div><h1>{article.title}</h1><p className="detail-lead">{article.description}</p><div className="detail-meta"><span><Clock3 size={14} /> {article.readTime} DK OKUMA</span><span><Target size={14} /> {article.metrics.join(" · ")}</span></div><nav className="detail-toc"><a href="#overview">Genel Çerçeve</a><a href="#master-method">Master Metodoloji</a><a href="#practice">Gözlem</a><a href="#coach">Metrikler</a><a href="#drills">Driller</a></nav><section id="overview"><h2>Teknik ve bilimsel çerçeve</h2><p>{article.content}</p><div className="summary-grid"><div><b>ANTRENÖR ODAĞI</b><p>{article.coachSummary}</p></div><div><b>SPORCU İÇİN</b><p>{article.athleteSummary}</p></div></div></section><section id="master-method" className="deep-library"><h2>Master Kütüphane Uygulama Çerçevesi</h2><div className="deep-section-grid">{article.deepSections.map((section) => <section className="deep-section" key={section.title}><h3>{section.title}</h3><p>{section.lead}</p><ul>{section.points.map((point) => <li key={point}>{point}</li>)}</ul></section>)}</div></section>{article.slug === "css" || article.slug === "css-calculation" ? <CssCalculator /> : null}<section id="practice"><h2>Uygulama ve gözlem</h2><ul>{article.observationPoints.map((point) => <li key={point}>{point}</li>)}</ul><div className="error-guide"><b>YAYGIN HATALAR</b>{article.commonErrors.map((error) => <span key={error}>· {error}</span>)}</div></section><section id="coach"><h2>Metrikler</h2><div className="metric-strip">{article.metrics.map((metric) => <span key={metric}><Gauge size={13} /> {metric}</span>)}</div></section><section id="drills"><h2>Drill ve set önerileri</h2><div className="drill-list">{article.drills.map((drill) => <div key={drill}><Dumbbell size={14} /><span>{drill}</span></div>)}</div></section><div className="related-content"><h2>İlgili konular</h2><div>{related.map((item) => <Link href={`/knowledge/${item.category}/${item.slug}`} key={item.slug}>{item.title}<span>→</span></Link>)}</div></div></article><AstraPanel article={article} /></div></main>;
}