import Link from "next/link";

export default function NotFound() {
  return <main className="route-not-found"><span className="eyebrow">ASTRA-G7 / ROUTE NOT FOUND</span><h1>Bu sayfa suyun dışında kaldı.</h1><p>Aradığın içerik mevcut route’larda bulunamadı. Bilgi tabanına veya SwimBase’e geri dönebilirsin.</p><div><Link href="/knowledge">Knowledge Base</Link><Link href="/swimbase">SwimBase</Link><Link href="/">Dashboard</Link></div></main>;
}
