"use client";

import { createContext, useContext, useEffect, useState } from "react";

export type Locale = "tr" | "en";

type Dictionary = {
  brand: string;
  commandDeck: string;
  athleteProfile: string;
  sessionArchive: string;
  nodeOnline: string;
  help: string;
  menu: string;
  language: string;
  welcome: string;
  welcomeBody: string;
  enterSystem: string;
  visionModule: string;
  trainBeyond: string;
  visible: string;
  liveFeed: string;
  simulationStable: string;
  tracking: string;
  athleteLane: string;
  poolLoad: string;
  nextSet: string;
  threshold: string;
  hydrodynamic: string;
  dragIndex: string;
  waterTemp: string;
  interactiveScene: string;
  dragToOrbit: string;
  cyberCoach: string;
  live: string;
  offline: string;
  telemetry: string;
  encrypted: string;
  heartRate: string;
  lactate: string;
  cssPace: string;
  systemReady: string;
  placeholder: string;
  connect: string;
  linkActive: string;
  endSession: string;
  tokenOptional: string;
  send: string;
  toolOutput: string;
  temporalLayer: string;
  warmup: string;
  recovery: string;
  signIn: string;
  signUp: string;
  signOut: string;
  athlete: string;
  coach: string;
  email: string;
  password: string;
  fullName: string;
  continueGoogle: string;
  saveProfile: string;
  profileSaved: string;
  cssHistory: string;
  performance: string;
  authTitle: string;
  authBody: string;
  close: string;
};

const dictionaries: Record<Locale, Dictionary> = {
  tr: {
    brand: "AQUA INTELLIGENCE",
    commandDeck: "KOMUTA GÜVERTESİ",
    athleteProfile: "SPORCU PROFİLİ",
    sessionArchive: "SEANS ARŞİVİ",
    nodeOnline: "DÜĞÜM 04 / ÇEVRİMİÇİ",
    help: "Yardım",
    menu: "Menü",
    language: "Dil",
    welcome: "SİBER ANTRENÖR",
    welcomeBody: "Biyometrik sinyallerin, teknik verilerin ve su altı zekasının kesiştiği komuta yüzeyi.",
    enterSystem: "SİSTEME GİR",
    visionModule: "GÖRÜ MODÜLÜ / HAVUZ 01",
    trainBeyond: "Görünenin",
    visible: "ötesinde çalış.",
    liveFeed: "CANLI AKIŞ",
    simulationStable: "SİMÜLASYON STABİL",
    tracking: "TAKİP",
    athleteLane: "SPORCU / KULVAR 04",
    poolLoad: "HAVUZ YÜKÜ",
    nextSet: "SONRAKİ SET",
    threshold: "EŞİK",
    hydrodynamic: "HİDRODİNAMİK MODEL v2.4",
    dragIndex: "SÜRÜKLEME ENDEKSİ",
    waterTemp: "SU SICAKLIĞI",
    interactiveScene: "ETKİLEŞİMLİ SAHNE",
    dragToOrbit: "YÖRÜNGE İÇİN SÜRÜKLE",
    cyberCoach: "Siber-Antrenör Konsolu",
    live: "CANLI",
    offline: "ÇEVRİMDIŞI",
    telemetry: "telemetri nominal",
    encrypted: "seans şifreli",
    heartRate: "NABIZ",
    lactate: "LAKTAT",
    cssPace: "CSS TEMPOSU",
    systemReady: "Siber-koç çekirdeği hazır. Antrenman verini bekliyorum.",
    placeholder: "Bir hedef veya antrenman sorusu yaz...",
    connect: "BAĞLANTI KUR",
    linkActive: "BAĞLANTI AKTİF",
    endSession: "SEANSI BİTİR",
    tokenOptional: "Yerel erişim anahtarı (isteğe bağlı)",
    send: "Mesaj gönder",
    toolOutput: "ARAÇ ÇIKTISI",
    temporalLayer: "4D ZAMANSAL KATMAN",
    warmup: "ISINMA",
    recovery: "TOPARLANMA",
    signIn: "GİRİŞ YAP",
    signUp: "KAYIT OL",
    signOut: "ÇIKIŞ",
    athlete: "Sporcu",
    coach: "Antrenör",
    email: "E-posta",
    password: "Şifre",
    fullName: "Ad soyad",
    continueGoogle: "Google ile devam et",
    saveProfile: "PROFİLİ KAYDET",
    profileSaved: "Profil kaydedildi",
    cssHistory: "CSS geçmişi",
    performance: "Kişisel performans",
    authTitle: "Kimlik doğrulama",
    authBody: "Profilini kişiselleştir ve seans verilerini aynı komuta yüzeyinde tut.",
    close: "Kapat",
  },
  en: {
    brand: "AQUA INTELLIGENCE",
    commandDeck: "COMMAND DECK",
    athleteProfile: "ATHLETE PROFILE",
    sessionArchive: "SESSION ARCHIVE",
    nodeOnline: "NODE 04 / ONLINE",
    help: "Help",
    menu: "Menu",
    language: "Language",
    welcome: "CYBER COACH",
    welcomeBody: "A command surface where biometric signals, technical data, and underwater intelligence converge.",
    enterSystem: "ENTER SYSTEM",
    visionModule: "VISION MODULE / POOL 01",
    trainBeyond: "Train beyond",
    visible: "the visible.",
    liveFeed: "LIVE FEED",
    simulationStable: "SIMULATION STABLE",
    tracking: "TRACKING",
    athleteLane: "ATHLETE / LANE 04",
    poolLoad: "POOL LOAD",
    nextSet: "NEXT SET",
    threshold: "THRESHOLD",
    hydrodynamic: "HYDRODYNAMIC MODEL v2.4",
    dragIndex: "DRAG INDEX",
    waterTemp: "WATER TEMP",
    interactiveScene: "INTERACTIVE SCENE",
    dragToOrbit: "DRAG TO ORBIT",
    cyberCoach: "Cyber-Coach Console",
    live: "LIVE",
    offline: "OFFLINE",
    telemetry: "telemetry nominal",
    encrypted: "session encrypted",
    heartRate: "HEART RATE",
    lactate: "LACTATE",
    cssPace: "CSS PACE",
    systemReady: "Cyber-Coach core is ready. Waiting for your training data.",
    placeholder: "Write a goal or training question...",
    connect: "CONNECT LINK",
    linkActive: "LINK ACTIVE",
    endSession: "END SESSION",
    tokenOptional: "Local access token (optional)",
    send: "Send message",
    toolOutput: "TOOL OUTPUT",
    temporalLayer: "4D TEMPORAL LAYER",
    warmup: "WARM-UP",
    recovery: "RECOVERY",
    signIn: "SIGN IN",
    signUp: "SIGN UP",
    signOut: "SIGN OUT",
    athlete: "Athlete",
    coach: "Coach",
    email: "Email",
    password: "Password",
    fullName: "Full name",
    continueGoogle: "Continue with Google",
    saveProfile: "SAVE PROFILE",
    profileSaved: "Profile saved",
    cssHistory: "CSS history",
    performance: "Personal performance",
    authTitle: "Identity access",
    authBody: "Personalize your profile and keep session data on the same command surface.",
    close: "Close",
  },
};

type I18nContextValue = { locale: Locale; setLocale: (locale: Locale) => void; t: Dictionary };
const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    if (typeof window === "undefined") return "tr";
    const saved = window.localStorage.getItem("cyber-coach-locale");
    return saved === "tr" || saved === "en" ? saved : "tr";
  });

  function setLocale(nextLocale: Locale) {
    setLocaleState(nextLocale);
    window.localStorage.setItem("cyber-coach-locale", nextLocale);
    document.documentElement.lang = nextLocale;
  }

  return <I18nContext.Provider value={{ locale, setLocale, t: dictionaries[locale] }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used inside I18nProvider");
  return context;
}
