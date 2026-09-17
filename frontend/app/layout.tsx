import type { Metadata } from "next";
import "./globals.css";
import { I18nProvider } from "./i18n";
import ThemeToggle from "@/components/ThemeToggle";

export const metadata: Metadata = {
  title: "Aqua Intelligence | Cyber-Coach",
  description: "3D/4D Siber-Antrenör kontrol yüzeyi",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="tr"><body><I18nProvider>{children}</I18nProvider><ThemeToggle /></body></html>;
}