"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Chrome, KeyRound, X } from "lucide-react";
import { FormEvent, useState } from "react";
import { useI18n } from "@/app/i18n";

export type Profile = {
  name: string;
  email: string;
  role: "athlete" | "coach";
  cssHistory: string;
  performance: string;
};

type AuthModalProps = {
  open: boolean;
  onClose: () => void;
  onAuthenticated: (profile: Profile) => void;
};

export default function AuthModal({ open, onClose, onAuthenticated }: AuthModalProps) {
  const { t } = useI18n();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [role, setRole] = useState<Profile["role"]>("athlete");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const profile: Profile = {
      name: name.trim() || email.split("@")[0] || (role === "coach" ? t.coach : t.athlete),
      email: email.trim() || "demo@aquaintelligence.local",
      role,
      cssHistory: "1:32 / 100M",
      performance: "12 seans · 68% havuz yükü",
    };
    window.localStorage.setItem("cyber-coach-profile", JSON.stringify(profile));
    onAuthenticated(profile);
    onClose();
  }

  function continueWithGoogle() {
    const googleAuthUrl = process.env.NEXT_PUBLIC_GOOGLE_AUTH_URL;
    if (!googleAuthUrl) throw new Error("NEXT_PUBLIC_GOOGLE_AUTH_URL is not configured.");
    window.location.assign(googleAuthUrl);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="auth-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={onClose}>
          <motion.section className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-title" initial={{ opacity: 0, scale: 0.94, y: 18 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.96, y: 10 }} onMouseDown={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={onClose} aria-label={t.close}><X size={17} /></button>
            <div className="eyebrow"><KeyRound size={13} /> AQUA ID / SECURE ACCESS</div>
            <h2 id="auth-title">{t.authTitle}</h2>
            <p className="auth-copy">{t.authBody}</p>
            <div className="auth-tabs"><button className={mode === "signin" ? "active" : ""} onClick={() => setMode("signin")}>{t.signIn}</button><button className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>{t.signUp}</button></div>
            <button className="google-button" type="button" onClick={continueWithGoogle}><Chrome size={16} /> {t.continueGoogle}</button>
            <div className="auth-divider"><span /> OR <span /></div>
            <form onSubmit={submit}>
              {mode === "signup" && <input value={name} onChange={(event) => setName(event.target.value)} placeholder={t.fullName} autoComplete="name" />}
              <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder={t.email} type="email" autoComplete="email" required />
              <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder={t.password} type="password" autoComplete={mode === "signin" ? "current-password" : "new-password"} required />
              <div className="role-picker"><button type="button" className={role === "athlete" ? "selected" : ""} onClick={() => setRole("athlete")}>{t.athlete}</button><button type="button" className={role === "coach" ? "selected" : ""} onClick={() => setRole("coach")}>{t.coach}</button></div>
              <button className="primary-action" type="submit">{mode === "signin" ? t.signIn : t.signUp} <span>↗</span></button>
            </form>
          </motion.section>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
