import { notFound } from "next/navigation";
import KnowledgeDetail from "@/components/knowledge/KnowledgeDetail";
import { getArticle, knowledgeArticles } from "@/components/knowledge/data";

export function generateStaticParams() {
  return knowledgeArticles.map((article) => ({ category: article.category, slug: article.slug }));
}

export default async function KnowledgeArticlePage({ params }: { params: Promise<{ category: string; slug: string }> }) {
  const { slug, category } = await params;
  const article = getArticle(slug);
  if (!article || article.category !== category) notFound();
  return <KnowledgeDetail article={article} />;
}
