"use client";

import { BookOpen, Search, Sparkles } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { knowledgeArticles, KnowledgeCategory } from "./data";

type KnowledgeLibraryProps = { initialCategory?: KnowledgeCategory | "all"; initialQuery?: string };
const filters: Array<[string, KnowledgeCategory | "all"]> = [["ALL", "all"], ["BIOMECHANICS", "biomechanics"], ["PHYSIOLOGY", "physiology"], ["TRAINING", "training"]];

export default function KnowledgeLibrary({ initialCategory = "biomechanics", initialQuery = "" }: KnowledgeLibraryProps) {
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState<KnowledgeCategory | "all">(initialCategory);
  const results = useMemo(() => knowledgeArticles.filter((article) => (category === "all" || article.category === category) && `${article.title} ${article.description}`.toLowerCase().includes(query.toLowerCase())), [category, query]);
  return <section className="module-page route-library"><header className="module-heading"><div><div className="eyebrow"><BookOpen size={13} /> SWIMBASE / KNOWLEDGE ENGINE</div><h1>SWIM <em>KNOWLEDGE BASE</em></h1><p>Her başlık; teknik açıklama, uygulama, drill, metrik ve Astra-G7 soru bağlamıyla ayrı bir detay sayfasına açılır.</p></div><div className="sync-badge sync-live"><i /> LAST SYNC: TODAY - WORLD AQUATICS UPDATED</div></header><div className="route-toolbar"><div className="knowledge-search"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="CSS, drag, high elbow, taper, VO2, SPM..." /></div><div className="category-tabs">{filters.map(([label, value]) => <button type="button" className={category === value ? "active" : ""} key={label} onClick={() => setCategory(value)}>{label}</button>)}</div></div><div className="library-count"><span><Sparkles size={13} /> {results.length} INDEXED ARTICLES</span><span>NO RESULT REDIRECTS / ROUTE SAFE</span></div><div className="route-article-grid">{results.map((article) => <Link className={`route-article-card ${article.category}`} href={`/knowledge/${article.category}/${article.slug}`} key={article.slug}><div className="article-meta"><span>{article.categoryLabel}</span><small>{article.readTime} MIN · {article.difficulty}</small></div><h2>{article.title}</h2><p>{article.description}</p><span className="card-link">OPEN ARTICLE <span>→</span></span></Link>)}{results.length === 0 && <div className="empty-state">Aramanızla eşleşen içerik bulunamadı.</div>}</div></section>;
}
