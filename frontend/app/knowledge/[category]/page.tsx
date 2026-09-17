import KnowledgeLibrary from "@/components/knowledge/KnowledgeLibrary";
import { KnowledgeCategory } from "@/components/knowledge/data";
import { notFound } from "next/navigation";

export default async function KnowledgeCategoryPage({ params }: { params: Promise<{ category: string }> }) {
  const { category } = await params;
  if (!["biomechanics", "physiology", "training"].includes(category)) notFound();
  const selected = category as KnowledgeCategory;
  return <KnowledgeLibrary initialCategory={selected} />;
}
