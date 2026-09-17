import KnowledgeLibrary from "@/components/knowledge/KnowledgeLibrary";

export default async function KnowledgePage({ searchParams }: { searchParams: Promise<{ query?: string }> }) {
  const { query = "" } = await searchParams;
  return <KnowledgeLibrary initialCategory="all" initialQuery={query} />;
}
