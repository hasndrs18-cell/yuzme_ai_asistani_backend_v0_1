"use client";

import { motion } from "framer-motion";
import { Award, CircleHelp, FileText, Gauge, Languages, UserRound, Waves } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import AuthModal, { Profile } from "@/components/auth/AuthModal";
import AcademyHome from "@/components/academy/AcademyHome";
import ElitePartnersPanel from "@/components/ElitePartnersPanel";
import CommunityExperiencePanel from "@/components/community/CommunityExperiencePanel";
import SwimbaseHero from "@/components/benefits/SwimbaseHero";
import { useI18n } from "./i18n";

export default function Home() {
  const { locale, setLocale, t } = useI18n();
  const [authOpen, setAuthOpen] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(() => {
    if (typeof window === "undefined") return null;
    const params = new URLSearchParams(window.location.search);
    if (params.get("access_token")) {
      return {
        name: params.get("profile_name") || "Google kullanıcısı",
        email: params.get("profile_email") || "",
        role: "athlete",
        cssHistory: "1:32 / 100M",
        performance: "Google hesabı bağlandı",
      };
    }
    const saved = window.localStorage.getItem("cyber-coach-profile");
    return saved ? JSON.parse(saved) as Profile : null;
  });
  const [partnersOpen, setPartnersOpen] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    if (accessToken) {
      window.localStorage.setItem("cyber-coach-access-token", accessToken);
      window.localStorage.setItem("cyber-coach-profile", JSON.stringify({
        name: params.get("profile_name") || "Google kullanıcısı",
        email: params.get("profile_email") || "",
        role: "athlete",
        cssHistory: "1:32 / 100M",
        performance: "Google hesabı bağlandı",
      } satisfies Profile));
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  function toggleLocale() {
    setLocale(locale === "tr" ? "en" : "tr");
  }

  return (
    <main className="app-shell">
      <nav className="topbar">
        <div className="brand"><span className="brand-mark"><Waves size={18} /></span><span>{t.brand.split(" ")[0]}<span className="brand-accent">/</span>INTELLIGENCE</span></div>
        <div className="nav-center"><Link className="nav-link" href="/athlete"><UserRound size={12} /> SPORCU</Link><Link className="nav-link" href="/coach"><UserRound size={12} /> ANTRENÖR</Link><Link className="nav-link" href="/academy"><BookOpenIcon /> ACADEMY</Link><Link className="nav-link" href="/knowledge-base"><FileText size={12} /> BİLGİ BANKASI</Link><Link className="nav-link" href="/swimbase"><Gauge size={12} /> SWIMBASE</Link><button className="nav-link" onClick={() => setPartnersOpen((open) => !open)}><Award size={12} /> REFERANSLAR</button></div>
        <div className="nav-right"><button className="hud-control" onClick={toggleLocale} aria-label={`${t.language}: ${locale.toUpperCase()}`}><Languages size={14} /> {locale.toUpperCase()}</button><button className="hud-control" onClick={() => setAuthOpen(true)} aria-label={profile ? profile.name : t.signIn}><UserRound size={14} /> {profile ? profile.name : t.signIn}</button><Link className="icon-button" href="/help" aria-label={t.help}><CircleHelp size={18} /></Link></div>
      </nav>
      <ElitePartnersPanel open={partnersOpen} onClose={() => setPartnersOpen(false)} />
      <SwimbaseHero />
      <AcademyHome />
      <CommunityExperiencePanel />
      <motion.footer className="status-footer" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><span>SWIMBASE</span><span>GERÇEK VERİ ÖNCELİĞİ</span><span className="footer-right">PROVIDER DURUMU GÖRÜNÜR <i /></span></motion.footer>
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} onAuthenticated={setProfile} />
    </main>
  );
}

function BookOpenIcon() { return <FileText size={12} />; }