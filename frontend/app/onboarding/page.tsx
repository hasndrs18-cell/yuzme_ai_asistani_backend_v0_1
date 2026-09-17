"use client";

import { ArrowRight, ShieldCheck, Waves } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function OnboardingPage() {
  const [role, setRole] = useState<"ATHLETE" | "COACH" | null>(null);
  const [saved, setSaved] = useState(false);
  async function saveRole(nextRole: "ATHLETE" | "COACH") {
    setRole(nextRole);
    const token = window.localStorage.getItem("cyber-coach-access-token");
    if (!token) return;
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
    const response = await fetch(`${backendUrl}/api/v1/onboarding/step`, { method: "PUT", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ role: nextRole, current_step: "role", data: { onboarding_role: nextRole } }) });
    setSaved(response.ok);
  }
  return <main className="onboarding-page"><div className="onboarding-mark"><Waves size={22} /></div><span className="eyebrow">SWIMBASE / ONBOARDING</span><h1>SwimBase&apos;i nasıl kullanacaksınız?</h1><p>Rolünüz, erişebileceğiniz verileri ve Astra-G7&apos;nin anlatım seviyesini belirler. Seçim backend onboarding state ile tamamlanır.</p><div className="onboarding-options"><button type="button" className={role === "ATHLETE" ? "selected" : ""} onClick={() => void saveRole("ATHLETE")}><strong>SPORCUYUM</strong><span>Profil, performans, wellness, readiness ve kişisel antrenman.</span></button><button type="button" className={role === "COACH" ? "selected" : ""} onClick={() => void saveRole("COACH")}><strong>ANTRENÖRÜM</strong><span>Takım, sporcu, plan, yük ve onay çalışma alanı.</span></button></div>{role && <div className="onboarding-next"><ShieldCheck size={15} /><span>{saved ? "Rol backend&apos;e kaydedildi." : "Rolü kaydetmek için giriş yapmanız gerekir."}</span>{saved && <Link href="/">DASHBOARD&apos;A GEÇ <ArrowRight size={14} /></Link>}</div>}</main>;
}
