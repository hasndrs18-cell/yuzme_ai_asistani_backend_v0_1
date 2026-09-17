"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Activity, ChevronRight, FileText, UserRound, X } from "lucide-react";

export type StudentProfile = {
  id: string;
  name: string;
  lane: string;
  status: string;
  lactate: string;
  css: string;
  focus: string;
  errors: string[];
};

export const studentProfiles: StudentProfile[] = [
  { id: "demo-student", name: "Deneme Öğrencisi", lane: "KULVAR 04", status: "CANLI", lactate: "3.8", css: "1:32", focus: "Nefes zamanlaması", errors: ["Baş rotasyonu", "Zayıf yakalama"] },
  { id: "selin-kaya", name: "Selin Kaya", lane: "KULVAR 02", status: "HAZIR", lactate: "2.9", css: "1:28", focus: "Yüksek dirsek", errors: ["Erken çekiş"] },
  { id: "mert-aydin", name: "Mert Aydın", lane: "KULVAR 06", status: "ARŞİV", lactate: "4.2", css: "1:36", focus: "Toparlanma ritmi", errors: ["Kalça düşüşü", "Geç nefes"] },
];

type StudentProfilesPanelProps = { open: boolean; selectedId: string; onSelect: (student: StudentProfile) => void; onClose: () => void };

export default function StudentProfilesPanel({ open, selectedId, onSelect, onClose }: StudentProfilesPanelProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.aside className="command-drawer student-drawer" initial={{ opacity: 0, x: 26 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 26 }} aria-label="Öğrenci dosyaları">
          <div className="drawer-header"><div><span className="eyebrow"><FileText size={13} /> DOSYA SİSTEMİ / 03</span><h2>ÖĞRENCİ DOSYALARI</h2></div><button className="drawer-close icon-button" onClick={onClose} aria-label="Paneli kapat"><X size={17} /></button></div>
          <p className="drawer-intro">Seçili sporcuya ait performans hafızası, laktat trendleri ve teknik hata kayıtları Astra-G7 analizine bağlandı.</p>
          <div className="student-list">
            {studentProfiles.map((student) => (
              <button key={student.id} className={`student-card ${selectedId === student.id ? "selected" : ""}`} onClick={() => onSelect(student)}>
                <span className="student-avatar"><UserRound size={17} /></span><span className="student-card-main"><b>{student.name}</b><small>{student.lane} · {student.status}</small><em>{student.focus}</em></span><ChevronRight size={15} />
              </button>
            ))}
          </div>
          <div className="student-memory"><div className="memory-label"><Activity size={13} /> SEÇİLİ HAFIZA</div><strong>{studentProfiles.find((student) => student.id === selectedId)?.name ?? "Öğrenci"}</strong><div className="memory-stats"><span>LAKTAT <b>{studentProfiles.find((student) => student.id === selectedId)?.lactate}</b></span><span>CSS <b>{studentProfiles.find((student) => student.id === selectedId)?.css}</b></span></div></div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
