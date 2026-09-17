"use client";

import { Camera, ChevronLeft, ChevronRight, FileVideo, Pause, Play, ScanLine, Upload, Waves } from "lucide-react";
import { ChangeEvent, useRef, useState } from "react";

type Sample = { name: string; discipline: string; duration: string; accent: string };
const samples: Sample[] = [
  { name: "Freestyle / Underwater Pull", discipline: "SERBEST · SIDE VIEW", duration: "00:18", accent: "cyan" },
  { name: "Butterfly / Recovery Phase", discipline: "KELEBEK · FRONT VIEW", duration: "00:12", accent: "coral" },
  { name: "Backstroke / Hip Line", discipline: "SIRT · OVERHEAD VIEW", duration: "00:21", accent: "violet" },
];

export default function VideoLab() {
  const [fileName, setFileName] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [status, setStatus] = useState<"EMPTY" | "UPLOADED" | "PROVIDER_NOT_CONNECTED">("EMPTY");
  const [playing, setPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  function selectSample(sample: Sample) {
    setFileName(sample.name);
    setStatus("PROVIDER_NOT_CONNECTED");
  }

  function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setVideoUrl(URL.createObjectURL(file));
    setStatus("UPLOADED");
  }

  function togglePlayback() {
    if (!videoRef.current) return;
    if (videoRef.current.paused) { void videoRef.current.play(); setPlaying(true); } else { videoRef.current.pause(); setPlaying(false); }
  }

  function stepFrame(direction: number) {
    if (!videoRef.current) return;
    videoRef.current.pause();
    videoRef.current.currentTime = Math.max(0, videoRef.current.currentTime + direction / 30);
    setPlaying(false);
  }

  return (
    <section className="module-page video-lab-page">
      <header className="module-heading"><div><div className="eyebrow"><Camera size={13} /> ASTRA-G7 / VISION PIPELINE</div><h1>VIDEO <em>LAB</em></h1><p>Canlı poz tahmini, su altı açıları ve hata sinyalleri tek analiz akışında.</p></div><div className="sync-badge"><i /> POSE ENGINE ONLINE / 30 FPS</div></header>
      <div className="video-lab-grid">
        <div className="video-workspace">
          <div className="video-stage">
            {videoUrl ? <video ref={videoRef} src={videoUrl} onEnded={() => setPlaying(false)} /> : <div className="sample-visual"><Waves size={42} /><span>{fileName || "Video seçilmedi"}</span><small>ANALYSIS PROVIDER REQUIRED</small></div>}
            {videoUrl && <div className="video-controls"><button type="button" onClick={() => stepFrame(-1)} aria-label="Bir kare geri"><ChevronLeft size={15} /></button><button type="button" onClick={togglePlayback} aria-label={playing ? "Videoyu duraklat" : "Videoyu oynat"}>{playing ? <Pause size={15} /> : <Play size={15} />}</button><button type="button" onClick={() => stepFrame(1)} aria-label="Bir kare ileri"><ChevronRight size={15} /></button></div>}
            {videoUrl && <div className="analysis-overlay" aria-label="Teknik analiz overlay"><i className="overlay-line line-shoulder" /><i className="overlay-line line-hip" /><b className="overlay-point point-shoulder" /><b className="overlay-point point-hip" /><span>ÖLÇÜM HAZIR</span></div>}
            <div className="video-stage-top"><span>{status === "PROVIDER_NOT_CONNECTED" ? "PROVIDER NOT CONNECTED" : status}</span><span>NO SYNTHETIC METRICS</span></div>
            <div className="video-stage-bottom"><span>{fileName || "Awaiting an authenticated upload"}</span></div>
          </div>
          <div className="upload-zone"><Upload size={19} /><div><b>DROP SWIM VIDEO HERE</b><span>MP4, MOV or WebM · max 500 MB</span></div><label className="outline-action">BROWSE FILE<input type="file" accept="video/*" onChange={handleUpload} /></label></div>
          <div className="sample-header"><span><FileVideo size={14} /> SAMPLE SWIM VIDEOS</span><small>SELECT A REFERENCE FEED</small></div>
          <div className="sample-grid">{samples.map((sample) => <button type="button" className={`sample-card ${sample.accent}`} key={sample.name} onClick={() => selectSample(sample)}><span className="sample-thumb"><Waves size={22} /><i>{sample.duration}</i></span><strong>{sample.name}</strong><small>{sample.discipline}</small></button>)}</div>
        </div>
        <aside className="analysis-console">
          <div className="console-title"><span><ScanLine size={14} /> VIDEO ANALYSIS</span><span className="provider-state">AI VIDEO ANALYSIS PROVIDER NOT CONNECTED</span></div>
          <div className="empty-console-state"><ScanLine size={16} /><strong>{status === "EMPTY" ? "Upload a swim video to begin" : status === "UPLOADED" ? "Video uploaded; analysis is not started" : "AI video analysis provider not connected"}</strong><span>No stroke rate, DPS, angles, observations or improvement claims are shown until a real provider returns measured results.</span></div>
          <div className="console-footer"><span>OBSERVATIONS: NOT AVAILABLE</span><span>CONFIDENCE: NOT AVAILABLE</span></div>
        </aside>
      </div>
    </section>
  );
}
