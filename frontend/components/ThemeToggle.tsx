"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [light, setLight] = useState(() => typeof window !== "undefined" && window.localStorage.getItem("swimbase-theme") === "light");
  useEffect(() => {
    document.documentElement.dataset.theme = light ? "light" : "dark";
  }, [light]);
  function toggle() {
    const next = !light;
    setLight(next);
    document.documentElement.dataset.theme = next ? "light" : "dark";
    window.localStorage.setItem("swimbase-theme", next ? "light" : "dark");
  }
  return <button type="button" className="theme-toggle" onClick={toggle} aria-label={light ? "Koyu temaya geç" : "Açık temaya geç"}>{light ? <Moon size={15} /> : <Sun size={15} />}</button>;
}
