import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Antrenman Paneli | SwimBase",
  description: "Günlük yüzme setlerini, CSS temposunu, nabız ve laktat verilerini takip et.",
};

export default function WorkoutsLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
