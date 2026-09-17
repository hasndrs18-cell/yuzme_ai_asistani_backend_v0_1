"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Award, Building2, ShieldCheck, UserRound, X } from "lucide-react";

type ElitePartnersPanelProps = { open: boolean; onClose: () => void };

const clubs = ["Fenerbahçe SK Yüzme Şubesi", "Galatasaray SK", "ENKA Spor Kulübü", "Olympic Training Centers"];
const experts = ["Elit Performans Antrenörleri", "Biyomekanik Analist Profilleri"];

export default function ElitePartnersPanel({ open, onClose }: ElitePartnersPanelProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.aside className="command-drawer partners-drawer" initial={{ opacity: 0, y: -18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} aria-label="Kullanan kulüpler ve referanslar">
          <div className="drawer-header"><div><span className="eyebrow"><Award size={13} /> PRESTİJ AĞI / 2026</span><h2>KULLANAN KULÜPLER & BAŞANTRENÖRLER</h2></div><button className="drawer-close icon-button" onClick={onClose} aria-label="Paneli kapat"><X size={17} /></button></div>
          <div className="partner-grid">{clubs.map((club, index) => <div className="partner-badge" key={club}><span className="partner-icon"><Building2 size={16} /></span><div><b>{club}</b><small>AKTİF PERFORMANS NODE {String(index + 1).padStart(2, "0")}</small></div><ShieldCheck size={14} /></div>)}</div>
          <div className="reference-strip"><span className="partner-icon"><UserRound size={16} /></span><div><small>BAŞANTRENÖRLER & PERFORMANS DİREKTÖRLERİ</small><strong>{experts.join("  /  ")}</strong></div></div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
