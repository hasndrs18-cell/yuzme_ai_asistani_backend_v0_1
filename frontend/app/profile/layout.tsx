import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sporcu Profili | SwimBase",
  description: "SwimBase sporcu profili, kişisel en iyi dereceler ve performans gelişim görünümü.",
};

export default function ProfileLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
