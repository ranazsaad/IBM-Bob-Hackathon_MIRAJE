"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  Github, Sparkles, Code, TestTube,
  Rocket, BookOpen, Loader2, AlertCircle, Zap,
  ArrowRight, Star, GitBranch, Mic, MicOff, Radio,
  CheckCircle2, Upload, Wifi, WifiOff, Send, Volume2, VolumeX,
  Bot, User as UserIcon,
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

type Tab = "github" | "chat" | "live";

interface ChatMessage {
  role: "user" | "Bob";
  content: string;
  timestamp: Date;
}

export default function Home() {
  const router = useRouter();
  const { setWorkspace } = useStore();
  const [activeTab, setActiveTab] = useState<Tab>("github");

  // GitHub state
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [depth, setDepth] = useState("shallow");

  // Chat with Bob state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState("");
  const [isBobSpeaking, setIsBobSpeaking] = useState(false);
  const [isChatListening, setIsChatListening] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);

  // Initialize welcome message for Bob
  useEffect(() => {
    setChatMessages([{
      role: "Bob",
      content: "Hi! I am Bob! I'm here to help you with anything you need; from coding questions and debugging to just hanging out and chatting. What's on your mind today?",
      timestamp: new Date()
    }]);
  }, []);

  const chatRecognitionRef = useRef<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

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
      mr.start(1000);
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

  // ── Browser SpeechRecognition for Live Meeting ──────────────────────────────────────
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
      if (recognitionRef.current) {
        try { recognition.start(); } catch (_) { }
      }
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsListening(true);
    setError(null);
  }, [liveNotes]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = null;
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
          } catch (_) { }
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

  // ── Bob Chat: Text-to-Speech ──────────────────────────────────────────────
  const speakText = useCallback((text: string) => {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Select a natural-sounding female voice
    const voices = window.speechSynthesis.getVoices();

    // Priority order for most natural female voices
    const preferredVoices = [
      'Samantha',           // macOS - very natural, warm
      'Ava',                // macOS - premium quality
      'Google UK English Female', // Chrome - natural British
      'Google US English',  // Chrome - natural American
      'Microsoft Zira',     // Windows - natural
      'Karen',              // macOS - friendly
      'Victoria',           // macOS - clear
      'Fiona',              // macOS - Scottish
      'Moira',              // macOS - Irish
      'Tessa',              // macOS - South African
    ];

    // Find the best available female voice
    let selectedVoice = voices.find(voice =>
      preferredVoices.some(preferred => voice.name.includes(preferred))
    );

    // Fallback: find any female voice
    if (!selectedVoice) {
      selectedVoice = voices.find(voice =>
        voice.name.toLowerCase().includes('female') ||
        voice.name.toLowerCase().includes('woman') ||
        (voice.name.includes('Google') && voice.lang.startsWith('en'))
      );
    }

    // Fallback: find any English voice that's not explicitly male
    if (!selectedVoice) {
      selectedVoice = voices.find(voice =>
        voice.lang.startsWith('en') &&
        !voice.name.toLowerCase().includes('male')
      );
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    // Optimized parameters for natural, human-like speech
    utterance.rate = 0.92;      // Slower, more conversational pace
    utterance.pitch = 1.2;      // Slightly higher for warm female voice
    utterance.volume = 0.85;    // Softer, more natural volume

    utterance.onstart = () => setIsBobSpeaking(true);
    utterance.onend = () => setIsBobSpeaking(false);
    utterance.onerror = () => setIsBobSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsBobSpeaking(false);
    }
  }, []);

  // ── Bob Chat: Speech Recognition ──────────────────────────────────────────
  const startChatListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Your browser doesn't support speech recognition. Please use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setUserInput(transcript);
      setIsChatListening(false);
    };

    recognition.onerror = (e: any) => {
      console.error("Speech recognition error:", e.error);
      setIsChatListening(false);
      if (e.error !== "no-speech") {
        setError(`Microphone error: ${e.error}`);
      }
    };

    recognition.onend = () => setIsChatListening(false);

    recognition.start();
    chatRecognitionRef.current = recognition;
    setIsChatListening(true);
    setError(null);
  }, []);

  const stopChatListening = useCallback(() => {
    if (chatRecognitionRef.current) {
      chatRecognitionRef.current.stop();
      chatRecognitionRef.current = null;
    }
    setIsChatListening(false);
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

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

  const handleSendMessage = async () => {
    if (!userInput.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: userInput.trim(),
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setUserInput("");
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userInput.trim(),
          conversation_history: chatMessages.map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          conversation_id: "Bob-chat",
          mode: "casual"
          // Let backend use its voice-optimized system prompt
        })
      });

      if (!response.ok) throw new Error("Failed to get response from Bob");

      const data = await response.json();
      const BobMessage: ChatMessage = {
        role: "Bob",
        content: data.response || "Oops! My brain just did a 404. Try again? 😅",
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, BobMessage]);

      if (autoSpeak && window.speechSynthesis) {
        speakText(BobMessage.content);
      }
    } catch (err: any) {
      setError(err.message || "Bob seems to be taking a coffee break ☕ Try again!");
      const errorMessage: ChatMessage = {
        role: "Bob",
        content: "Whoops! Something went wrong on my end. 😅 Can you try that again?",
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
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
        {activeTab === "chat" && <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-purple-600/5 rounded-full blur-3xl" />}
      </div>

      {/* Header */}
      <header className="relative border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/boblogo.png"
              alt="Bob Logo"
              width={40}
              height={40}
              className="rounded-lg"
            />
            <span className="font-display text-xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent tracking-tight">
              Bob By Your Side
            </span>
          </div>
          <span className="font-mono text-[10px] text-purple-400 bg-purple-900/20 px-3 py-1.5 rounded border border-purple-500/30 tracking-widest uppercase">
            POWERED BY IBM BOB
          </span>
        </div>
      </header>

      {/* Hero */}
      <section className="relative container mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 text-[11px] font-mono text-purple-400 bg-purple-900/30 border border-purple-700/40 px-4 py-2 rounded-full mb-8 tracking-[0.2em] uppercase">
          <Star className="w-3 h-3" /> AI DevFlow IDE
        </div>
        <h1 className="font-display text-5xl md:text-7xl font-extrabold mb-6 leading-[1.05] tracking-tighter text-white">
          Your AI <em className="not-italic text-transparent bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text">Engineering</em><br />Teammate
        </h1>
        <div className="max-w-2xl mx-auto mb-12 space-y-6">
          <p className="text-[17px] text-gray-400 font-medium border-l-[3px] border-purple-500 pl-5 text-left mx-auto max-w-xl leading-relaxed">
            <strong className="text-gray-100 font-semibold">Developers don't struggle to write code.</strong><br />
            They struggle to understand existing codebases.
          </p>
          <p className="text-[15px] text-gray-400 leading-relaxed max-w-xl mx-auto">
            Paste a GitHub URL. Bob By Your Side clones, analyzes, and explains
            your repository.. architecture, evolution, bugs, tests, and docs<br />
            <span className="text-teal-400 font-medium"> IBM Bob</span> reads the full codebase, not just snippets.
          </p>
        </div>

        {/* Input Card */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 shadow-2xl shadow-black/40">

            {/* 3-tab switcher */}
            <div className="flex gap-1.5 mb-6 p-1 bg-gray-800 rounded-xl">
              {([
                { id: "github", label: "GitHub Repo", icon: <Github className="w-3.5 h-3.5" />, active: "bg-blue-600 shadow-blue-500/30" },
                { id: "chat", label: "Chat with Bob", icon: <Bot className="w-3.5 h-3.5" />, active: "bg-purple-600 shadow-purple-500/30" },
                { id: "live", label: "Live Meeting", icon: <Mic className="w-3.5 h-3.5" />, active: "bg-red-600 shadow-red-500/30" },
              ] as const).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setError(null); }}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-medium text-xs transition-all shadow-lg ${activeTab === tab.id ? `${tab.active} text-white` : "text-gray-400 hover:text-white"
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

            {/* ── Chat with Bob tab ── */}
            {activeTab === "chat" && (
              <div className="space-y-4">
                {/* Chat messages */}
                <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4 h-[400px] overflow-y-auto space-y-3">
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`flex gap-3 animate-fade-in ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-lg overflow-hidden ${msg.role === "Bob"
                        ? "bg-gray-800 shadow-purple-500/20 border border-purple-500/30"
                        : "bg-gradient-to-br from-blue-500 to-cyan-500 shadow-blue-500/20"
                        }`}>
                        {msg.role === "Bob" ? (
                          <img src="/Pop.png" alt="Bob Avatar" className="w-full h-full object-cover" />
                        ) : (
                          <UserIcon className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div className={`flex flex-col max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
                        <div className={`inline-block px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.role === "Bob"
                          ? "bg-gray-800/80 border border-gray-700/50 text-gray-200 rounded-tl-sm"
                          : "bg-blue-600 border border-blue-500 text-white rounded-tr-sm"
                          }`}>
                          {msg.content}
                        </div>
                        <div className="text-[10px] text-gray-500 mt-1.5 px-1 font-medium tracking-wide">
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>

                {/* Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={autoSpeak ? stopSpeaking : undefined}
                    className={`p-2 rounded-lg transition-colors ${isBobSpeaking
                      ? "bg-purple-600 text-white animate-pulse"
                      : autoSpeak
                        ? "bg-purple-900/40 border border-purple-700/40 text-purple-300 hover:bg-purple-900/60"
                        : "bg-gray-700 text-gray-400 hover:bg-gray-600"
                      }`}
                    title={autoSpeak ? "Auto-speak enabled" : "Auto-speak disabled"}
                  >
                    {isBobSpeaking ? <Volume2 className="w-4 h-4" /> : autoSpeak ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setAutoSpeak(!autoSpeak)}
                    className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    {autoSpeak ? "Disable" : "Enable"} voice
                  </button>
                </div>

                {/* Input */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={isChatListening ? stopChatListening : startChatListening}
                    disabled={loading}
                    className={`p-3 rounded-xl transition-all ${isChatListening
                      ? "bg-purple-600 text-white animate-pulse shadow-purple-500/30 shadow-lg"
                      : "bg-gray-700 hover:bg-gray-600 text-white"
                      } disabled:opacity-50`}
                  >
                    {isChatListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </button>
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    placeholder="Type or speak your message..."
                    disabled={loading}
                    className="flex-1 bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 outline-none focus:border-purple-500/70 transition-colors disabled:opacity-50"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!userInput.trim() || loading}
                    className="p-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 text-white hover:opacity-90 transition-all shadow-lg shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </button>
                </div>

                <div className="bg-purple-900/20 border border-purple-700/30 rounded-xl p-3 text-xs text-purple-300">
                  💡 <strong>Tip:</strong> Bob is your casual AI buddy! Ask about code, get tech advice, or just chat. Click the mic to speak or type your message.
                </div>
              </div>
            )}

            {/* ── Live Meeting tab ── */}
            {activeTab === "live" && (
              <div className="space-y-4">
                {/* Status badges */}
                <div className="flex gap-2 flex-wrap">
                  <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${sttStatus?.bob_api_configured
                    ? "bg-green-900/30 border-green-700/40 text-green-300"
                    : "bg-red-900/30 border-red-700/40 text-red-300"
                    }`}>
                    {sttStatus?.bob_api_configured ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                    Bob API {sttStatus?.bob_api_configured ? "Connected" : "Not configured"}
                  </span>
                  <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${sttStatus?.watson_stt_available
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
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all ${isListening
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
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all disabled:opacity-50 ${isRecordingAudio
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
                    className={`w-full bg-gray-800 border rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 outline-none resize-none transition-colors ${isListening ? "border-red-500/60 focus:border-red-400" : "border-gray-600 focus:border-red-500/70"
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

// Made with Bob
