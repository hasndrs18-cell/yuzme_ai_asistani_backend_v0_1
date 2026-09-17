"use client";

import { Chrome, Heart, MessageCircle, Send, Share2, UsersRound } from "lucide-react";
import { FormEvent, useState } from "react";

type Post = { id: number; author: string; kind: string; text: string; likes: number; liked: boolean };
const initialPosts: Post[] = [
  { id: 1, author: "Selin Kaya", kind: "AÇIK SU ANTRENMANI", text: "Kıyıdan 2.000 m navigasyon setinde her 6 kulaçta bir baş kaldırmayı denedim. Rüzgâr yönünü takip etmek beklediğimden daha önemliymiş.", likes: 12, liked: false },
  { id: 2, author: "Mert Aydın", kind: "BESLENME & TOPARLANMA", text: "Uzun seans sonrası su ve karbonhidrat planımı not ederek paylaşacağım. Aynı mesafeyi yüzenlerin deneyimlerini merak ediyorum.", likes: 8, liked: false },
];

function googleLoginUrl() {
  return process.env.NEXT_PUBLIC_GOOGLE_AUTH_URL || `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/auth/google`;
}

export default function CommunityExperiencePanel() {
  const [posts, setPosts] = useState<Post[]>(initialPosts);
  const [text, setText] = useState("");
  const [kind, setKind] = useState("ANTRENMAN PROGRAMI");
  const [signedIn] = useState(() => typeof window !== "undefined" && Boolean(window.localStorage.getItem("cyber-coach-access-token") || window.localStorage.getItem("cyber-coach-profile")));
  const [notice, setNotice] = useState("");

  function share(event: FormEvent) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    setPosts((current) => [{ id: Date.now(), author: "Sen", kind, text: trimmed, likes: 0, liked: false }, ...current]);
    setText("");
    setNotice("Deneyimin topluluk akışına eklendi.");
  }

  function like(id: number) {
    setPosts((current) => current.map((post) => post.id === id ? { ...post, liked: !post.liked, likes: post.likes + (post.liked ? -1 : 1) } : post));
  }

  return <section className="community-panel" aria-labelledby="community-title">
    <div className="community-heading"><div><span className="section-kicker"><UsersRound size={13} /> TOPLULUK & DENEYİM</span><h2 id="community-title">Suyun içindeki deneyimini paylaş.</h2><p>Antrenman programını, beslenme düzenini veya açık su notlarını Google hesabınla güvenli biçimde topluluğa aktar.</p></div><Share2 size={28} /></div>
    {!signedIn ? <div className="community-signin"><div><strong>Paylaşım yapmak için hesabını bağla</strong><span>Google / Gmail ile giriş yaptığında gönderilerin hesabınla ilişkilendirilir.</span></div><a className="google-community-button" href={googleLoginUrl()}><Chrome size={16} /> GOOGLE İLE BAĞLAN</a></div> : <form className="community-composer" onSubmit={share}><div className="composer-row"><select value={kind} onChange={(event) => setKind(event.target.value)} aria-label="Paylaşım türü"><option>ANTRENMAN PROGRAMI</option><option>BESLENME DÜZENİ</option><option>AÇIK SU DENEYİMİ</option></select><span>Google hesabınla paylaşım açık</span></div><textarea value={text} onChange={(event) => setText(event.target.value)} placeholder="Bugünkü setini, rotanı veya toparlanma deneyimini yaz..." rows={3} /><button type="submit" disabled={!text.trim()}><Send size={15} /> TOPLULUKTA PAYLAŞ</button>{notice && <small className="community-notice">{notice}</small>}</form>}
    <div className="community-feed">{posts.map((post) => <article className="community-post" key={post.id}><div className="post-meta"><strong>{post.author}</strong><span>{post.kind}</span></div><p>{post.text}</p><div className="post-actions"><button type="button" onClick={() => like(post.id)} className={post.liked ? "liked" : ""}><Heart size={14} /> {post.likes}</button><button type="button" onClick={() => setNotice("Yanıt özelliği için gönderi sahibiyle bağlantı kurulacak.")}><MessageCircle size={14} /> YANITLA</button><a href={`mailto:?subject=SwimBase deneyimi&body=${encodeURIComponent(post.text)}`}><Send size={14} /> GMAİL&apos;DE PAYLAŞ</a></div></article>)}</div>
  </section>;
}
