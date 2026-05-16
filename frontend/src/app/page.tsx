"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Github, FileText, Sparkles, Code, TestTube,
  Rocket, BookOpen, Loader2, AlertCircle, Zap,
  ArrowRight, Star, GitBranch, Mic, MicOff, Radio,
  CheckCircle2, Upload, Wifi, WifiOff,
} from "lucide-react";
import { api } from "@/lib/api";
import { useStore } from "@/lib/store";

const EXAMPLE_REPOS = [
  { label: "facebook/react", url: "https://github.com/facebook/react" },
  { label: "fastapi/fastapi", url: "https://github.com/tiangolo/fastapi" },
  { label: "vercel/next.js", url: "https://github.com/vercel/next.js" },
];

const FEATURES = [
  { icon: <Sparkles className="w-5 h-5" />, title: "Illustration Mode", desc: "Architecture diagrams, dependency maps & visual explanations", color: "from-blue-600 to-cyan-500", bg: "bg-blue-950/40 border-blue-800/40" },
  { icon: <Code className="w-5 h-5" />, title: "Development Mode", desc: "Code review, security analysis & refactoring suggestions", color: "from-purple-600 to-pink-500", bg: "bg-purple-950/40 border-purple-800/40" },
  { icon: <TestTube className="w-5 h-5" />, title: "Testing Mode", desc: "Unit tests, integration tests & coverage analysis", color: "from-green-600 to-emerald-500", bg: "bg-green-950/40 border-green-800/40" },
  { icon: <Rocket className="w-5 h-5" />, title: "Deployment Mode", desc: "Docker, CI/CD pipelines & Kubernetes configs", color: "from-orange-600 to-amber-500", bg: "bg-orange-950/40 border-orange-800/40" },
  { icon: <BookOpen className="w-5 h-5" />, title: "Documentation Mode", desc: "README, API docs & onboarding guides", color: "from-pink-600 to-rose-500", bg: "bg-pink-950/40 border-pink-800/40" },
  { icon: <Radio className="w-5 h-5" />, title: "Live Meeting", desc: "Join a meeting live — AI takes notes & extracts requirements in real-time", color: "from-red-500 to-orange-400", bg: "bg-red-950/40 border-red-800/40" },
];

// ─── Speech Recognition types ────────────────────────────────────────────────
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

type Tab = "github" | "transcript" | "live";

export default function Home() {
  const router = useRouter();
  const { setWorkspace } = useStore();
  const [activeTab, setActiveTab] = useState<Tab>("github");
  // GitHub state
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [depth, setDepth] = useState("shallow");
  // Transcript state
  const [transcript, setTranscript] = useState("");
  const [context, setContext] = useState("");
  // Live meeting state
  const [isListening, setIsListening] = useState(false);
  const [liveNotes, setLiveNotes] = useState("");
  const [meetingTitle, setMeetingTitle] = useState("");
  const [meetingContext, setMeetingContext] = useState("");
  const [liveInsights, setLiveInsights] = useState<{ key_topics: string[]; action_items: string[]; insights: string[] } | null>(null);
  const [insightLoading, setInsightLoading] = useState(false);
  const [sttStatus, setSttStatus] = useState<{ watson_stt_available: boolean; bob_api_configured: boolean } | null>(null);
  const [isRecordingAudio, setIsRecordingAudio] = useState(false);
  const [uploadingAudio, setUploadingAudio] = useState(false);
  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const insightTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Common state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Check Watson STT status on mount ────────────────────────────────────
  useEffect(() => {
    fetch("http://localhost:8000/api/live-meeting/stt-status")
      .then((r) => r.json())
      .then(setSttStatus)
      .catch(() => setSttStatus({ watson_stt_available: false, bob_api_configured: false }));
  }, []);

  // ── Watson STT: MediaRecorder audio upload ────────────────────────────────
  const startAudioRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mr.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      mr.start(1000); // collect chunks every second
      mediaRecorderRef.current = mr;
      setIsRecordingAudio(true);
      setError(null);
    } catch {
      setError("Microphone access denied. Please allow microphone in browser settings.");
    }
  }, []);

  const stopAndTranscribeAudio = useCallback(async () => {
    const mr = mediaRecorderRef.current;
    if (!mr) return;
    mr.stop();
    mr.stream.getTracks().forEach((t) => t.stop());
    mediaRecorderRef.current = null;
    setIsRecordingAudio(false);
    setUploadingAudio(true);
    try {
      const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const form = new FormData();
      form.append("audio", blob, "meeting.webm");
      form.append("language", "en-US");
      const res = await fetch("http://localhost:8000/api/live-meeting/transcribe", {
        method: "POST", body: form,
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Transcription failed");
      const data = await res.json();
      if (data.transcript) setLiveNotes((prev) => prev + (prev ? "\n" : "") + data.transcript);
      else setError("No speech detected in recording.");
    } catch (err: any) {
      setError(err.message || "Watson STT transcription failed.");
    } finally {
      setUploadingAudio(false);
      audioChunksRef.current = [];
    }
  }, []);

  // ── Browser SpeechRecognition setup ──────────────────────────────────────
  const startListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Your browser doesn't support speech recognition. Please use Chrome or Edge.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    let finalText = liveNotes;

    recognition.onresult = (event: any) => {
      let interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += t + " ";
        } else {
          interimTranscript += t;
        }
      }
      setLiveNotes(finalText + interimTranscript);
    };

    recognition.onerror = (e: any) => {
      console.error("Speech recognition error:", e.error);
      if (e.error !== "no-speech") {
        setError(`Microphone error: ${e.error}. Check permissions.`);
        setIsListening(false);
      }
    };

    recognition.onend = () => {
      // Auto-restart if still supposed to be listening
      if (recognitionRef.current) {
        try { recognition.start(); } catch (_) {}
      }
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsListening(true);
    setError(null);
  }, [liveNotes]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = null; // prevent auto-restart
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  // Poll for quick insights every 40 s while mic is active
  useEffect(() => {
    if (isListening) {
      insightTimerRef.current = setInterval(async () => {
        if (liveNotes.length > 100) {
          setInsightLoading(true);
          try {
            const res = await fetch("http://localhost:8000/api/live-meeting/quick-insights", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ partial_notes: liveNotes }),
            });
            if (res.ok) setLiveInsights(await res.json());
          } catch (_) {}
          setInsightLoading(false);
        }
      }, 40_000);
    } else {
      if (insightTimerRef.current) clearInterval(insightTimerRef.current);
    }
    return () => { if (insightTimerRef.current) clearInterval(insightTimerRef.current); };
  }, [isListening, liveNotes]);

  // Cleanup on unmount
  useEffect(() => () => stopListening(), [stopListening]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleAnalyzeRepo = async () => {
    if (!repoUrl.trim()) return;
    setLoading(true); setError(null);
    try {
      const result: any = await api.analyzeGitHub({ repo_url: repoUrl, branch, depth });
      setWorkspace({ workspace_id: result.workspace_id, type: "github", metadata: result.metadata || {}, created_at: result.created_at || new Date().toISOString() });
      router.push(`/workspace?workspace_id=${result.workspace_id}&type=github`);
    } catch (err: any) {
      setError(err.message || "Failed to analyze repository. Check your OpenAI API key in backend/.env");
    } finally { setLoading(false); }
  };

  const handleAnalyzeTranscript = async () => {
    if (!transcript.trim()) return;
    setLoading(true); setError(null);
    try {
      const result: any = await api.analyzeTranscript({ transcript, context });
      setWorkspace({ workspace_id: result.workspace_id, type: "transcript", metadata: result.requirements ? { requirements: result.requirements } : {}, created_at: result.created_at || new Date().toISOString() });
      router.push(`/workspace?workspace_id=${result.workspace_id}&type=transcript`);
    } catch (err: any) {
      setError(err.message || "Failed to process transcript. Check your OpenAI API key in backend/.env");
    } finally { setLoading(false); }
  };

  const handleProcessLiveMeeting = async () => {
    if (!liveNotes.trim()) return;
    stopListening();
    setLoading(true); setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/live-meeting/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_notes: liveNotes, meeting_title: meetingTitle || "Meeting", context: meetingContext }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Failed to process meeting");
      const result = await res.json();
      setWorkspace({
        workspace_id: result.workspace_id,
        type: "transcript",
        metadata: { requirements: result.requirements, user_stories: result.user_stories, tickets: result.tickets },
        created_at: result.processed_at || new Date().toISOString(),
      });
      router.push(`/workspace?workspace_id=${result.workspace_id}&type=transcript`);
    } catch (err: any) {
      setError(err.message || "Failed to process meeting notes.");
    } finally { setLoading(false); }
  };

  // ── UI ────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-3xl" />
        {activeTab === "live" && <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-red-600/5 rounded-full blur-3xl animate-pulse" />}
      </div>

      {/* Header */}
      <header className="relative border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              DevPilot AI
            </span>
          </div>
          <span className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full border border-gray-700">
            v1.0.0 · Hackathon MVP
          </span>
        </div>
      </header>

      {/* Hero */}
      <section className="relative container mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 text-xs text-blue-400 bg-blue-900/30 border border-blue-700/40 px-4 py-2 rounded-full mb-8">
          <Star className="w-3 h-3" /> AI-Powered Developer IDE
        </div>
        <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight">
          Your AI{" "}
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Engineering
          </span>{" "}
          Teammate
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-12">
          Analyze GitHub repos, process meeting transcripts, or join live meetings.
          Get instant AI insights for code review, testing, deployment, and documentation.
        </p>

        {/* Input Card */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 shadow-2xl shadow-black/40">

            {/* 3-tab switcher */}
            <div className="flex gap-1.5 mb-6 p-1 bg-gray-800 rounded-xl">
              {([
                { id: "github", label: "GitHub Repo", icon: <Github className="w-3.5 h-3.5" />, active: "bg-blue-600 shadow-blue-500/30" },
                { id: "transcript", label: "Transcript", icon: <FileText className="w-3.5 h-3.5" />, active: "bg-purple-600 shadow-purple-500/30" },
                { id: "live", label: "Live Meeting", icon: <Mic className="w-3.5 h-3.5" />, active: "bg-red-600 shadow-red-500/30" },
              ] as const).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setError(null); }}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-medium text-xs transition-all shadow-lg ${
                    activeTab === tab.id ? `${tab.active} text-white` : "text-gray-400 hover:text-white"
                  }`}
                >
                  {tab.icon}{tab.label}
                </button>
              ))}
            </div>

            {/* Error */}
            {error && (
              <div className="mb-4 flex items-start gap-2 bg-red-900/20 border border-red-700/40 rounded-xl p-3">
                <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <p className="text-xs text-red-300">{error}</p>
              </div>
            )}

            {/* ── GitHub tab ── */}
            {activeTab === "github" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-gray-400 font-medium mb-1.5">Repository URL</label>
                  <div className="flex items-center gap-2 bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 focus-within:border-blue-500/70 transition-colors">
                    <Github className="w-4 h-4 text-gray-500 shrink-0" />
                    <input
                      type="text" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)}
                      placeholder="https://github.com/username/repository"
                      className="flex-1 bg-transparent text-sm text-white placeholder-gray-500 outline-none"
                      onKeyDown={(e) => e.key === "Enter" && handleAnalyzeRepo()}
                    />
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {EXAMPLE_REPOS.map((r) => (
                      <button key={r.url} onClick={() => setRepoUrl(r.url)}
                        className="flex items-center gap-1 text-xs text-gray-500 hover:text-blue-400 transition-colors">
                        <GitBranch className="w-3 h-3" />{r.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-400 font-medium mb-1.5">Branch</label>
                    <input type="text" value={branch} onChange={(e) => setBranch(e.target.value)}
                      placeholder="main"
                      className="w-full bg-gray-800 border border-gray-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-blue-500/70 transition-colors" />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 font-medium mb-1.5">Depth</label>
                    <select value={depth} onChange={(e) => setDepth(e.target.value)}
                      className="w-full bg-gray-800 border border-gray-600 rounded-xl px-4 py-2.5 text-sm text-white outline-none focus:border-blue-500/70 transition-colors">
                      <option value="shallow">Shallow (Fast)</option>
                      <option value="deep">Deep (Thorough)</option>
                    </select>
                  </div>
                </div>
                <button onClick={handleAnalyzeRepo} disabled={!repoUrl.trim() || loading}
                  className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-500 text-white px-6 py-3.5 rounded-xl font-medium hover:opacity-90 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed">
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Analyzing…</> : <><Zap className="w-4 h-4" />Analyze Repository<ArrowRight className="w-4 h-4" /></>}
                </button>
              </div>
            )}

            {/* ── Transcript tab ── */}
            {activeTab === "transcript" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-gray-400 font-medium mb-1.5">Meeting Notes or Transcript</label>
                  <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste your meeting notes, transcript, or requirements here…"
                    rows={6}
                    className="w-full bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 outline-none focus:border-purple-500/70 transition-colors resize-none" />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 font-medium mb-1.5">Context (Optional)</label>
                  <input type="text" value={context} onChange={(e) => setContext(e.target.value)}
                    placeholder="e.g. Sprint planning for Q2 2026"
                    className="w-full bg-gray-800 border border-gray-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-purple-500/70 transition-colors" />
                </div>
                <button onClick={handleAnalyzeTranscript} disabled={!transcript.trim() || loading}
                  className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-500 text-white px-6 py-3.5 rounded-xl font-medium hover:opacity-90 transition-all shadow-lg shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed">
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Processing…</> : <><Zap className="w-4 h-4" />Process Transcript<ArrowRight className="w-4 h-4" /></>}
                </button>
              </div>
            )}

            {/* ── Live Meeting tab ── */}
            {activeTab === "live" && (
              <div className="space-y-4">
                {/* Status badges */}
                <div className="flex gap-2 flex-wrap">
                  <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
                    sttStatus?.bob_api_configured
                      ? "bg-green-900/30 border-green-700/40 text-green-300"
                      : "bg-red-900/30 border-red-700/40 text-red-300"
                  }`}>
                    {sttStatus?.bob_api_configured ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                    Bob API {sttStatus?.bob_api_configured ? "Connected" : "Not configured"}
                  </span>
                  <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
                    sttStatus?.watson_stt_available
                      ? "bg-blue-900/30 border-blue-700/40 text-blue-300"
                      : "bg-gray-800 border-gray-700 text-gray-500"
                  }`}>
                    <Mic className="w-3 h-3" />
                    Watson STT {sttStatus?.watson_stt_available ? "Ready" : "Not configured"}
                  </span>
                </div>

                {/* Meeting info */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-400 font-medium mb-1.5">Meeting Title</label>
                    <input type="text" value={meetingTitle} onChange={(e) => setMeetingTitle(e.target.value)}
                      placeholder="Sprint Planning Q2"
                      className="w-full bg-gray-800 border border-gray-600 rounded-xl px-3 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-red-500/70 transition-colors" />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 font-medium mb-1.5">Context</label>
                    <input type="text" value={meetingContext} onChange={(e) => setMeetingContext(e.target.value)}
                      placeholder="E.g. e-commerce app"
                      className="w-full bg-gray-800 border border-gray-600 rounded-xl px-3 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-red-500/70 transition-colors" />
                  </div>
                </div>

                {/* Mic controls */}
                <div className="space-y-2">
                  <label className="block text-xs text-gray-400 font-medium">Recording</label>
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Browser SpeechRecognition */}
                    <button
                      onClick={isListening ? stopListening : startListening}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all ${
                        isListening
                          ? "bg-red-600 hover:bg-red-700 text-white animate-pulse shadow-red-500/30 shadow-lg"
                          : "bg-gray-700 hover:bg-gray-600 text-white"
                      }`}>
                      {isListening ? <><MicOff className="w-4 h-4" />Stop</> : <><Mic className="w-4 h-4" />Live (Browser)</>}
                    </button>

                    {/* Watson STT audio upload */}
                    {sttStatus?.watson_stt_available && (
                      <button
                        onClick={isRecordingAudio ? stopAndTranscribeAudio : startAudioRecording}
                        disabled={uploadingAudio || isListening}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all disabled:opacity-50 ${
                          isRecordingAudio
                            ? "bg-blue-600 hover:bg-blue-700 text-white animate-pulse shadow-blue-500/30 shadow-lg"
                            : "bg-blue-900/40 hover:bg-blue-900/60 border border-blue-700/40 text-blue-300"
                        }`}>
                        {uploadingAudio
                          ? <><Loader2 className="w-4 h-4 animate-spin" />Transcribing…</>
                          : isRecordingAudio
                          ? <><MicOff className="w-4 h-4" />Stop + Transcribe (Watson)</>
                          : <><Upload className="w-4 h-4" />Record (Watson STT)</>}
                      </button>
                    )}

                    {isListening && (
                      <span className="flex items-center gap-1.5 text-xs text-red-400">
                        <span className="w-2 h-2 rounded-full bg-red-500 animate-ping inline-block" />
                        Listening…
                      </span>
                    )}
                  </div>
                  {!sttStatus?.watson_stt_available && (
                    <p className="text-xs text-gray-600">Add <code className="bg-gray-800 px-1 rounded">WATSON_STT_API_KEY</code> to .env to enable high-accuracy IBM Watson transcription</p>
                  )}
                </div>

                {/* Live transcript box */}
                <div className="relative">
                  <label className="block text-xs text-gray-400 font-medium mb-1.5">Live Notes</label>
                  <textarea
                    value={liveNotes} onChange={(e) => setLiveNotes(e.target.value)}
                    placeholder="Your speech will appear here in real-time. You can also type or paste text directly…"
                    rows={6}
                    className={`w-full bg-gray-800 border rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 outline-none resize-none transition-colors ${
                      isListening ? "border-red-500/60 focus:border-red-400" : "border-gray-600 focus:border-red-500/70"
                    }`}
                  />
                  {liveNotes && (
                    <span className="absolute bottom-3 right-3 text-xs text-gray-600">{liveNotes.split(" ").filter(Boolean).length} words</span>
                  )}
                </div>

                {/* Quick insights panel */}
                {liveInsights && (
                  <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-semibold text-gray-300">
                      {insightLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3 text-yellow-400" />}
                      Live Insights
                    </div>
                    {liveInsights.key_topics?.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Key Topics</p>
                        <div className="flex flex-wrap gap-1.5">
                          {liveInsights.key_topics.map((t, i) => (
                            <span key={i} className="text-xs bg-blue-900/40 border border-blue-700/40 text-blue-300 px-2 py-0.5 rounded-full">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {liveInsights.action_items?.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Action Items</p>
                        <ul className="space-y-1">
                          {liveInsights.action_items.slice(0, 4).map((item, i) => (
                            <li key={i} className="flex items-start gap-1.5 text-xs text-gray-300">
                              <CheckCircle2 className="w-3 h-3 text-green-400 mt-0.5 shrink-0" />{item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Tip */}
                {!isListening && !liveNotes && (
                  <div className="bg-amber-900/20 border border-amber-700/30 rounded-xl p-3 text-xs text-amber-300">
                    💡 <strong>Tip:</strong> Click "Start Recording" to let the AI listen to your meeting via microphone. Works best in Chrome or Edge. You can also paste notes directly.
                  </div>
                )}

                {/* Process button */}
                <button
                  onClick={handleProcessLiveMeeting}
                  disabled={!liveNotes.trim() || loading}
                  className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-red-600 to-orange-500 text-white px-6 py-3.5 rounded-xl font-medium hover:opacity-90 transition-all shadow-lg shadow-red-500/20 disabled:opacity-50 disabled:cursor-not-allowed">
                  {loading
                    ? <><Loader2 className="w-4 h-4 animate-spin" />Extracting Requirements…</>
                    : <><Sparkles className="w-4 h-4" />Analyze Meeting & Extract Requirements<ArrowRight className="w-4 h-4" /></>}
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative container mx-auto px-6 py-16 border-t border-gray-800">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-3">5 AI Modes + Live Meeting</h2>
          <p className="text-gray-400">Each mode is fine-tuned for a specific engineering workflow</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          {FEATURES.map((f, i) => (
            <div key={i} className={`${f.bg} border rounded-2xl p-5 hover:scale-[1.02] transition-transform cursor-default`}>
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 shadow-lg`}>
                {f.icon}
              </div>
              <h3 className="font-semibold text-white mb-1">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="container mx-auto px-6 text-center text-xs text-gray-600">
          DevPilot AI · Built for Hackathon 2026 · Powered by OpenAI GPT-4o + RAG
        </div>
      </footer>
    </div>
  );
}
