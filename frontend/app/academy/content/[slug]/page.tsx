import AcademyContentDetail from "@/components/academy/AcademyContentDetail";

export default async function AcademyContentPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <AcademyContentDetail slug={slug} />;
}
