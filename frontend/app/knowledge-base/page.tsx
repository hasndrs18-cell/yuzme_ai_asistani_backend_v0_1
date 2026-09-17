import KnowledgeLibrary from "@/components/knowledge/KnowledgeLibrary";

export const metadata = {
  title: "Swim Knowledge Base | SwimBase",
  description: "Yüzme tekniği, fizyoloji ve antrenman metodolojisi için kaynaklı bilgi bankası.",
};

export default function KnowledgeBasePage() {
  return <KnowledgeLibrary initialCategory="all" />;
}
