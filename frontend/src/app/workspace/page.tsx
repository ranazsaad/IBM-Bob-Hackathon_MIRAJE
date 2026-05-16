"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import {
  Sparkles, Code, TestTube, Rocket, BookOpen, FileText,
  Send, ArrowLeft, Copy, Download, Check, Loader2,
  ChevronRight, GitBranch, Star, Files, Zap, History,
  AlertCircle, X, RefreshCw, Eye, Layout, ClipboardList,
  CheckCircle2, ChevronDown, ChevronUp, ExternalLink, FolderGit2,
} from "lucide-react";
import { useStore, AIMode, QueryHistoryItem } from "@/lib/store";
import { api, ModeQueryRequest } from "@/lib/api";

// Dynamically import Monaco Editor (heavy, no SSR)
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

// ─── Types ────────────────────────────────────────────────────────────────────

interface ModeConfig {
  id: AIMode;
  label: string;
  icon: React.ReactNode;
  color: string;
  gradient: string;
  glow: string;
  description: string;
  prompts: string[];
}

// ─── Constants ────────────────────────────────────────────────────────────────

const MODES: ModeConfig[] = [
  {
    id: "illustration",
    label: "Illustration",
    icon: <Layout className="w-4 h-4" />,
    color: "text-blue-400",
    gradient: "from-blue-600 to-cyan-500",
    glow: "shadow-blue-500/30",
    description: "Architecture diagrams & visual explanations",
    prompts: [
      "Generate an architecture diagram of this codebase",
      "Show me the data flow between components",
      "Create a dependency map",
      "Explain the folder structure visually",
    ],
  },
  {
    id: "development",
    label: "Development",
    icon: <Code className="w-4 h-4" />,
    color: "text-purple-400",
    gradient: "from-purple-600 to-pink-500",
    glow: "shadow-purple-500/30",
    description: "Code review, debugging & refactoring",
    prompts: [
      "Review the code quality and suggest improvements",
      "Find security vulnerabilities",
      "Identify performance bottlenecks",
      "Suggest architectural refactoring",
    ],
  },
  {
    id: "testing",
    label: "Testing",
    icon: <TestTube className="w-4 h-4" />,
    color: "text-green-400",
    gradient: "from-green-600 to-emerald-500",
    glow: "shadow-green-500/30",
    description: "Unit tests, integration tests & coverage",
    prompts: [
      "Generate unit tests for the main module",
      "Create integration test scenarios",
      "Identify untested edge cases",
      "Generate mock objects for external APIs",
    ],
  },
  {
    id: "deployment",
    label: "Deployment",
    icon: <Rocket className="w-4 h-4" />,
    color: "text-orange-400",
    gradient: "from-orange-600 to-amber-500",
    glow: "shadow-orange-500/30",
    description: "Docker, CI/CD & infrastructure configs",
    prompts: [
      "Generate a production Dockerfile",
      "Create a GitHub Actions CI/CD pipeline",
      "Generate docker-compose for development",
      "Create Kubernetes deployment manifests",
    ],
  },
  {
    id: "documentation",
    label: "Documentation",
    icon: <BookOpen className="w-4 h-4" />,
    color: "text-pink-400",
    gradient: "from-pink-600 to-rose-500",
    glow: "shadow-pink-500/30",
    description: "README, API docs & onboarding guides",
    prompts: [
      "Generate a comprehensive README",
      "Create API documentation",
      "Write an onboarding guide for new developers",
      "Generate technical architecture overview",
    ],
  },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function MermaidRenderer({ content }: { content: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [rendered, setRendered] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    const match = content.match(/```mermaid\n([\s\S]*?)\n```/);
    const diagram = match ? match[1] : content;

    import("mermaid").then((m) => {
      m.default.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
      m.default.render("mermaid-svg-" + Date.now(), diagram)
        .then(({ svg }) => {
          if (ref.current) {
            // Remove any error messages from mermaid output
            const cleanSvg = svg.replace(/Syntax error in text[\s\S]*?mermaid version[\s\S]*?$/i, '');
            ref.current.innerHTML = cleanSvg;
            setRendered(true);
          }
        })
        .catch(() => setError(true));
    });
  }, [content]);

  if (error) {
    return (
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
        <pre className="text-sm text-gray-300 overflow-auto">{content}</pre>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-700 p-6 overflow-auto">
      <div ref={ref} className="flex justify-center [&_text]:!fill-gray-200 [&_text]:!font-medium" />
      {!rendered && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
        </div>
      )}
    </div>
  );
}

function ResultDisplay({ item, mode }: { item: QueryHistoryItem; mode: AIMode }) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<"rendered" | "raw">("rendered");

  const handleCopy = () => {
    navigator.clipboard.writeText(item.result.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = item.result.type === "code" ? "txt" : "md";
    const blob = new Blob([item.result.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `devpilot-${mode}-result.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isMermaid = item.result.content.includes("```mermaid") ||
                    item.result.content.includes("graph ") ||
                    item.result.content.includes("sequenceDiagram") ||
                    item.result.content.includes("classDiagram");

  // Only treat as pure code if it's explicitly marked as code/config AND doesn't contain markdown formatting
  const isCode = (item.result.type === "code" || item.result.type === "config") &&
                 !item.result.content.includes("```") &&
                 !item.result.content.includes("#");

  return (
    <div className="flex flex-col gap-4 animate-fade-in">
      {/* Result header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
            {item.result.type}
          </span>
          {item.result.metadata?.language && (
            <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
              {item.result.metadata.language}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {(isMermaid || isCode) && (
            <button
              onClick={() => setViewMode(v => v === "rendered" ? "raw" : "rendered")}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-white px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Eye className="w-3 h-3" />
              {viewMode === "rendered" ? "Raw" : "Preview"}
            </button>
          )}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-white px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
            {copied ? "Copied!" : "Copy"}
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-white px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <Download className="w-3 h-3" />
            Save
          </button>
        </div>
      </div>

      {/* Main content */}
      {isMermaid && viewMode === "rendered" ? (
        <MermaidRenderer content={item.result.content} />
      ) : isCode && viewMode === "rendered" ? (
        <div className="rounded-xl overflow-hidden border border-gray-700 h-96">
          <MonacoEditor
            height="100%"
            defaultLanguage="python"
            value={item.result.content}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: "on",
              scrollBeyondLastLine: false,
              wordWrap: "on",
            }}
          />
        </div>
      ) : (
        <div className="bg-gray-900/50 rounded-xl border border-gray-700/50 p-8 max-h-[70vh] overflow-auto">
          <div className="markdown-body">
            <style dangerouslySetInnerHTML={{__html: `
              .markdown-body * {
                background: transparent !important;
                background-color: transparent !important;
              }
              .markdown-body code {
                background: rgba(31, 41, 55, 0.6) !important;
                background-color: rgba(31, 41, 55, 0.6) !important;
              }
              .markdown-body pre {
                background: transparent !important;
                background-color: transparent !important;
              }
              .markdown-body pre code {
                background: transparent !important;
                background-color: transparent !important;
              }
              .markdown-body pre > div {
                background: #0d1117 !important;
                background-color: #0d1117 !important;
              }
            `}} />
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
              code({ node, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                const language = match ? match[1] : '';
                const codeString = String(children).replace(/\n$/, '');
                const inline = !className || !language;
                
                // Block code with syntax highlighting
                if (!inline && language) {
                  return (
                    <div className="relative group my-6 not-prose">
                      <div className="absolute right-3 top-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(codeString);
                          }}
                          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white px-2.5 py-1.5 bg-gray-800/90 hover:bg-gray-700 rounded-md transition-colors backdrop-blur-sm"
                        >
                          <Copy className="w-3.5 h-3.5" />
                          Copy
                        </button>
                      </div>
                      <SyntaxHighlighter
                        style={vscDarkPlus as any}
                        language={language}
                        PreTag="div"
                        customStyle={{
                          margin: 0,
                          borderRadius: '0.75rem',
                          background: '#0d1117',
                          padding: '1.25rem',
                          border: '1px solid rgba(55, 65, 81, 0.5)',
                          fontSize: '0.875rem',
                          lineHeight: '1.6',
                        }}
                        showLineNumbers={codeString.split('\n').length > 5}
                        wrapLines={true}
                        {...props}
                      >
                        {codeString}
                      </SyntaxHighlighter>
                    </div>
                  );
                }
                
                // Inline code
                return (
                  <code className="bg-gray-800/60 text-cyan-300 px-2 py-0.5 rounded-md text-sm font-mono border border-gray-700/50" {...props}>
                    {children}
                  </code>
                );
              },
              pre({ children }) {
                return <>{children}</>;
              },
              h1({ children }) {
                return <h1 className="text-3xl font-bold text-white mt-8 mb-5 pb-3 border-b border-gray-700/50 first:mt-0">{children}</h1>;
              },
              h2({ children }) {
                return <h2 className="text-2xl font-bold text-white mt-8 mb-4 pb-2 border-b border-gray-700/30">{children}</h2>;
              },
              h3({ children }) {
                return <h3 className="text-xl font-semibold text-white mt-6 mb-3">{children}</h3>;
              },
              h4({ children }) {
                return <h4 className="text-lg font-semibold text-gray-200 mt-5 mb-2">{children}</h4>;
              },
              h5({ children }) {
                return <h5 className="text-base font-semibold text-gray-300 mt-4 mb-2">{children}</h5>;
              },
              h6({ children }) {
                return <h6 className="text-sm font-semibold text-gray-400 mt-3 mb-2">{children}</h6>;
              },
              p({ children }) {
                return <p className="text-gray-300 leading-relaxed mb-4 text-[15px]">{children}</p>;
              },
              ul({ children }) {
                return <ul className="list-disc ml-6 text-gray-300 space-y-2 mb-5 marker:text-gray-500">{children}</ul>;
              },
              ol({ children }) {
                return <ol className="list-decimal ml-6 text-gray-300 space-y-2 mb-5 marker:text-gray-500">{children}</ol>;
              },
              li({ children }) {
                return <li className="text-gray-300 leading-relaxed pl-2">{children}</li>;
              },
              a({ href, children }) {
                return (
                  <a
                    href={href}
                    className="text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 hover:decoration-blue-300 transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {children}
                  </a>
                );
              },
              blockquote({ children }) {
                return (
                  <blockquote className="border-l-4 border-blue-500/50 bg-gray-800/30 pl-5 pr-4 py-3 italic text-gray-400 my-5 rounded-r-lg">
                    {children}
                  </blockquote>
                );
              },
              strong({ children }) {
                return <strong className="font-semibold text-white">{children}</strong>;
              },
              em({ children }) {
                return <em className="italic text-gray-300">{children}</em>;
              },
              hr() {
                return <hr className="border-gray-700/50 my-8" />;
              },
              table({ children }) {
                return (
                  <div className="overflow-x-auto my-6 rounded-lg border border-gray-700/50">
                    <table className="min-w-full divide-y divide-gray-700/50">
                      {children}
                    </table>
                  </div>
                );
              },
              thead({ children }) {
                return <thead className="bg-gray-800/50">{children}</thead>;
              },
              tbody({ children }) {
                return <tbody className="divide-y divide-gray-700/30 bg-gray-900/20">{children}</tbody>;
              },
              tr({ children }) {
                return <tr className="hover:bg-gray-800/30 transition-colors">{children}</tr>;
              },
              th({ children }) {
                return <th className="px-5 py-3 text-left text-sm font-semibold text-white">{children}</th>;
              },
              td({ children }) {
                return <td className="px-5 py-3 text-sm text-gray-300">{children}</td>;
              },
            }}
          >
              {item.result.content}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Explanation */}
      {item.result.explanation && (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700/50 p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Explanation</p>
          </div>
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              className="text-sm text-gray-300 leading-relaxed space-y-3"
              components={{
                p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc list-inside space-y-2 ml-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside space-y-2 ml-2">{children}</ol>,
                li: ({ children }) => <li className="text-gray-300 leading-relaxed">{children}</li>,
                strong: ({ children }) => <strong className="text-blue-400 font-semibold">{children}</strong>,
                em: ({ children }) => <em className="text-cyan-400">{children}</em>,
                code: ({ children }) => (
                  <code className="bg-gray-900/60 text-cyan-400 px-1.5 py-0.5 rounded text-xs font-mono">
                    {children}
                  </code>
                ),
                h3: ({ children }) => <h3 className="text-base font-semibold text-gray-200 mt-4 mb-2">{children}</h3>,
                h4: ({ children }) => <h4 className="text-sm font-semibold text-gray-300 mt-3 mb-2">{children}</h4>,
              }}
            >
              {item.result.explanation}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Meeting Results Panel ─────────────────────────────────────────────────────

function MeetingResultsPanel({
  metadata, onImplement, onScaffoldProject, scaffoldingProject
}: {
  metadata: any;
  onImplement: (query: string) => void;
  onScaffoldProject: (reqs: string[], tickets: any[]) => void;
  scaffoldingProject: boolean;
}) {
  const [expanded, setExpanded] = useState(true);
  const requirements: string[] = metadata.requirements || [];
  const tickets: any[]         = metadata.tickets || [];

  if (!requirements.length && !tickets.length) return null;

  return (
    <div className="mb-6 bg-gray-900 border border-indigo-700/40 rounded-2xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-3 bg-indigo-900/30 hover:bg-indigo-900/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <ClipboardList className="w-4 h-4 text-indigo-400" />
          <span className="text-sm font-semibold text-indigo-200">Meeting Requirements &amp; Plan</span>
          <span className="text-xs bg-indigo-800/60 text-indigo-300 px-2 py-0.5 rounded-full">
            {requirements.length} requirements · {tickets.length} tickets
          </span>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-indigo-400" /> : <ChevronDown className="w-4 h-4 text-indigo-400" />}
      </button>

      {expanded && (
        <div className="p-5 space-y-5">
          {/* Requirements */}
          {requirements.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">Extracted Requirements</p>
              <ul className="space-y-2">
                {requirements.map((req: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                    <span className="text-sm text-gray-300">{req}</span>
                    <button
                      onClick={() => onImplement(`Help me implement this requirement: ${req}`)}
                      className="ml-auto shrink-0 text-xs text-indigo-400 hover:text-indigo-300 bg-indigo-900/30 hover:bg-indigo-900/50 border border-indigo-700/40 px-2 py-0.5 rounded-lg transition-colors"
                    >
                      Implement →
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tickets */}
          {tickets.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">Engineering Tickets</p>
              <div className="grid md:grid-cols-2 gap-3">
                {tickets.slice(0, 6).map((ticket: any, i: number) => (
                  <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-3">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                        ticket.priority === "critical" ? "bg-red-900/50 text-red-300" :
                        ticket.priority === "high"     ? "bg-orange-900/50 text-orange-300" :
                        ticket.priority === "medium"   ? "bg-yellow-900/50 text-yellow-300" :
                                                         "bg-gray-700 text-gray-400"
                      }`}>{ticket.priority || "medium"}</span>
                      <span className="text-xs text-gray-500">{ticket.estimate || "TBD"}</span>
                    </div>
                    <p className="text-sm text-white font-medium mb-1 line-clamp-2">{ticket.title}</p>
                    <p className="text-xs text-gray-400 line-clamp-2">{ticket.description}</p>
                    <button
                      onClick={() => onImplement(`Help me start implementing this ticket: ${ticket.title}. Description: ${ticket.description}`)}
                      className="mt-2 w-full text-xs text-indigo-400 hover:text-indigo-300 bg-indigo-900/20 hover:bg-indigo-900/40 border border-indigo-700/30 py-2 rounded-lg transition-colors"
                    >
                      Start Implementing
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Scaffold Full Project Button */}
          <div className="pt-4 border-t border-gray-800">
            <button
              onClick={() => onScaffoldProject(requirements, tickets)}
              disabled={scaffoldingProject}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-500 text-white px-6 py-3.5 rounded-xl font-medium hover:opacity-90 transition-all shadow-lg shadow-green-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scaffoldingProject ? (
                <><Loader2 className="w-5 h-5 animate-spin" />Scaffolding Full Project...</>
              ) : (
                <><FolderGit2 className="w-5 h-5" />Scaffold Entire Project in VS Code</>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main Workspace Page ───────────────────────────────────────────────────────

function WorkspaceContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const {
    workspace, setWorkspace,
    currentMode, setMode,
    history, addToHistory,
    currentResult, setCurrentResult,
    isQuerying, setIsQuerying,
    error, setError,
    currentConversation, setCurrentConversation,
    conversations, setConversations,
  } = useStore();

  const [query, setQuery] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const [vscodeLoading, setVscodeLoading] = useState(false);
  const [vscodeStatus, setVscodeStatus] = useState<string | null>(null);
  const [scaffoldingProject, setScaffoldingProject] = useState(false);
  const [setupGuide, setSetupGuide] = useState<string | null>(null);
  const [debugErrorText, setDebugErrorText] = useState("");
  const [isDebugging, setIsDebugging] = useState(false);
  const [debugResult, setDebugResult] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const modeConfig = MODES.find((m) => m.id === currentMode)!;

  // Handle VS Code integration
  const handleOpenInVSCode = async () => {
    if (!workspace) return;
    
    setVscodeLoading(true);
    setVscodeStatus(null);
    
    try {
      const result: any = await api.openWorkspace(workspace.workspace_id);
      
      if (result.vscode_url) {
        // Open VS Code
        window.location.href = result.vscode_url;
        setVscodeStatus(`✅ Opening in VS Code: ${result.workspace_path}`);
      } else {
        setVscodeStatus(`✅ ${result.message}`);
      }
    } catch (err: any) {
      setVscodeStatus(`❌ ${err.message || "Failed to open in VS Code"}`);
    } finally {
      setVscodeLoading(false);
    }
  };

  const handleScaffoldProject = async (requirements: string[], tickets: any[]) => {
    if (!workspace) return;
    setScaffoldingProject(true);
    setError(null);
    setSetupGuide(null);
    setDebugResult(null);
    try {
      const result: any = await api.scaffoldProject(workspace.workspace_id, requirements, tickets);
      if (result.setup_guide) {
        setSetupGuide(result.setup_guide);
      }
      if (result.vscode_url) {
        window.location.href = result.vscode_url;
      }
    } catch (err: any) {
      setError(err.message || "Failed to scaffold project.");
    } finally {
      setScaffoldingProject(false);
    }
  };

  const handleDebugError = async () => {
    if (!workspace || !debugErrorText.trim()) return;
    setIsDebugging(true);
    setDebugResult(null);
    try {
      const result: any = await api.debugError(workspace.workspace_id, debugErrorText);
      setDebugResult(result.action);
    } catch (err: any) {
      setDebugResult(`❌ Error debugging: ${err.message}`);
    } finally {
      setIsDebugging(false);
    }
  };

  // Load workspace from URL params if not in store
  useEffect(() => {
    const wsId = searchParams.get("workspace_id");
    const type = searchParams.get("type") as "github" | "transcript";

    if (wsId && !workspace) {
      api.getWorkspace(wsId)
        .then((data: any) => setWorkspace({ ...data, type }))
        .catch(() => {
          // Build a placeholder workspace so the UI still renders
          setWorkspace({
            workspace_id: wsId,
            type: type || "github",
            metadata: { repo_name: "Repository", language: "Unknown" },
            created_at: new Date().toISOString(),
          });
        });
    }
  }, [searchParams, workspace, setWorkspace]);

  // Submit a query
  const handleSubmit = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim() || !workspace) return;

    setIsQuerying(true);
    setError(null);
    setQuery("");

    try {
      // Save user message to conversation
      if (currentConversation) {
        await api.addMessage(currentConversation.id, {
          role: "user",
          content: q,
          metadata: { mode: currentMode },
        });
      }

      const payload: ModeQueryRequest = {
        workspace_id: workspace.workspace_id,
        query: q,
      };

      const response = await api.queryMode(currentMode, payload);

      // Save assistant response to conversation
      if (currentConversation) {
        await api.addMessage(currentConversation.id, {
          role: "assistant",
          content: response.result.content,
          metadata: {
            mode: currentMode,
            type: response.result.type,
            suggestions: response.suggestions,
          },
        });
      }

      const historyItem: QueryHistoryItem = {
        id: Date.now().toString(),
        mode: currentMode,
        query: q,
        result: response.result,
        suggestions: response.suggestions,
        timestamp: new Date(),
      };

      addToHistory(historyItem);
      setCurrentResult(historyItem);
    } catch (err: any) {
      setError(err.message || "Something went wrong. Check your OpenAI API key and backend connection.");
    } finally {
      setIsQuerying(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (!workspace) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-gray-400">Loading workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* ── Top Bar ── */}
      <header className="border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Left: Logo + workspace info */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/")}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${modeConfig.gradient} flex items-center justify-center`}>
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-white">DevPilot AI</span>
            </div>
            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-gray-700">
              {workspace.type === "github" ? (
                <GitBranch className="w-4 h-4 text-gray-400" />
              ) : (
                <FileText className="w-4 h-4 text-gray-400" />
              )}
              <span className="text-sm text-gray-300 font-medium">
                {workspace.metadata.repo_name || "Meeting Analysis"}
              </span>
              {workspace.metadata.language && (
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">
                  {workspace.metadata.language}
                </span>
              )}
              {workspace.metadata.file_count && (
                <span className="flex items-center gap-1 text-xs text-gray-500">
                  <Files className="w-3 h-3" />
                  {workspace.metadata.file_count} files
                </span>
              )}
            </div>
          </div>

          {/* Right: History toggle */}
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <History className="w-4 h-4" />
            <span className="hidden md:inline">History</span>
            {history.length > 0 && (
              <span className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {Math.min(history.length, 9)}
              </span>
            )}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* ── Left Sidebar: Mode Selector ── */}
        <aside className="w-14 md:w-56 border-r border-gray-800 bg-gray-950 flex flex-col pt-4 shrink-0">
          <div className="px-2 md:px-3 mb-2">
            <p className="hidden md:block text-xs text-gray-500 uppercase tracking-wider font-medium mb-3 px-2">
              AI Modes
            </p>
            <nav className="flex flex-col gap-1">
              {MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => { setMode(mode.id); setCurrentResult(null); }}
                  className={`
                    flex items-center gap-3 px-2 md:px-3 py-2.5 rounded-xl transition-all text-left
                    ${currentMode === mode.id
                      ? `bg-gradient-to-r ${mode.gradient} bg-opacity-20 text-white shadow-lg ${mode.glow}`
                      : "text-gray-400 hover:text-white hover:bg-gray-800/60"}
                  `}
                >
                  <span className={currentMode === mode.id ? "text-white" : mode.color}>
                    {mode.icon}
                  </span>
                  <div className="hidden md:block overflow-hidden">
                    <p className="text-sm font-medium truncate">{mode.label}</p>
                  </div>
                  {currentMode === mode.id && (
                    <ChevronRight className="w-3 h-3 ml-auto hidden md:block shrink-0" />
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Workspace summary */}
          {workspace.metadata.description && (
            <div className="hidden md:block mt-auto p-3 border-t border-gray-800">
              <p className="text-xs text-gray-500 leading-relaxed line-clamp-4">
                {workspace.metadata.description}
              </p>
            </div>
          )}
        </aside>

        {/* ── Main Content Area ── */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Mode header */}
          <div className={`px-6 py-4 border-b border-gray-800 bg-gradient-to-r ${modeConfig.gradient} bg-opacity-5`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${modeConfig.gradient} flex items-center justify-center shadow-lg ${modeConfig.glow}`}>
                  {modeConfig.icon}
                </div>
                <div>
                  <h2 className="font-bold text-white">{modeConfig.label} Mode</h2>
                  <p className="text-xs text-gray-400">{modeConfig.description}</p>
                </div>
              </div>
              
              {/* VS Code Integration Button (only for GitHub workspaces in Development mode) */}
              {workspace.type === "github" && currentMode === "development" && (
                <div className="flex flex-col items-end gap-2">
                  <button
                    onClick={handleOpenInVSCode}
                    disabled={vscodeLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors shadow-lg"
                  >
                    {vscodeLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Opening...</span>
                      </>
                    ) : (
                      <>
                        <FolderGit2 className="w-4 h-4" />
                        <span>Open in VS Code</span>
                        <ExternalLink className="w-3 h-3" />
                      </>
                    )}
                  </button>
                  {vscodeStatus && (
                    <p className="text-xs text-gray-400 max-w-xs text-right">{vscodeStatus}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Content area */}
          <div className="flex-1 overflow-auto p-6">
            {/* Meeting results panel */}
            {workspace.type === "transcript" && (
              <MeetingResultsPanel
                metadata={workspace.metadata}
                onImplement={(q) => {
                  setMode("development");
                  handleSubmit(q);
                }}
                onScaffoldProject={handleScaffoldProject}
                scaffoldingProject={scaffoldingProject}
              />
            )}

            {/* Setup Guide & Debugging Panel */}
            {setupGuide && (
              <div className="mb-6 bg-gray-900 border border-green-700/40 rounded-2xl overflow-hidden animate-fade-in">
                <div className="px-5 py-3 bg-green-900/30 border-b border-green-700/40 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-semibold text-green-200">Project Scaffolded Successfully</span>
                </div>
                
                <div className="p-5 space-y-6">
                  {/* Setup Guide */}
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-blue-400" /> Step-by-Step Guide
                    </h3>
                    <div className="prose prose-sm prose-invert max-w-none bg-gray-800/50 p-4 rounded-xl border border-gray-700/50">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{setupGuide}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Bob Error Assistant */}
                  <div className="border-t border-gray-800 pt-6">
                    <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-amber-400" /> Faced an error in VS Code?
                    </h3>
                    <p className="text-xs text-gray-400 mb-3">
                      Paste your terminal error below. Bob will read your local project files and tell you exactly how to fix it.
                    </p>
                    <textarea
                      value={debugErrorText}
                      onChange={(e) => setDebugErrorText(e.target.value)}
                      placeholder="Paste terminal output here..."
                      rows={4}
                      className="w-full bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 outline-none focus:border-amber-500/70 transition-colors resize-y mb-3"
                    />
                    <button
                      onClick={handleDebugError}
                      disabled={!debugErrorText.trim() || isDebugging}
                      className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-amber-600 to-orange-500 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:opacity-90 transition-all disabled:opacity-50"
                    >
                      {isDebugging ? <><Loader2 className="w-4 h-4 animate-spin" /> Bob is debugging...</> : <><Zap className="w-4 h-4" /> Ask Bob to Fix Error</>}
                    </button>

                    {debugResult && (
                      <div className="mt-4 p-4 bg-gray-800 border border-amber-700/40 rounded-xl">
                        <h4 className="text-xs font-semibold text-amber-400 mb-2 uppercase tracking-wider">Bob's Required Action</h4>
                        <div className="prose prose-sm prose-invert max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{debugResult}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Error banner */}
            {error && (
              <div className="mb-4 flex items-start gap-3 bg-red-900/20 border border-red-700/40 rounded-xl p-4">
                <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <p className="text-sm text-red-300">{error}</p>
                </div>
                <button onClick={() => setError(null)}>
                  <X className="w-4 h-4 text-red-400 hover:text-red-300" />
                </button>
              </div>
            )}

            {/* Loading state */}
            {isQuerying && (
              <div className="flex flex-col items-center justify-center py-20 gap-4">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${modeConfig.gradient} flex items-center justify-center shadow-2xl ${modeConfig.glow} animate-pulse`}>
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <div className="text-center">
                  <p className="text-white font-medium">DevPilot AI is thinking...</p>
                  <p className="text-sm text-gray-500 mt-1">Analyzing your codebase with RAG pipeline</p>
                </div>
                <div className="flex gap-1 mt-2">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full bg-gradient-to-br ${modeConfig.gradient} animate-bounce`}
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Result */}
            {!isQuerying && currentResult && (
              <ResultDisplay item={currentResult} mode={currentMode} />
            )}

            {/* Suggestions from last result */}
            {!isQuerying && currentResult?.suggestions && currentResult.suggestions.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Follow-up suggestions</p>
                <div className="flex flex-wrap gap-2">
                  {currentResult.suggestions.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleSubmit(s)}
                      className="text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-500 px-3 py-1.5 rounded-lg transition-all"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Empty state */}
            {!isQuerying && !currentResult && (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className={`w-20 h-20 rounded-3xl bg-gradient-to-br ${modeConfig.gradient} flex items-center justify-center shadow-2xl ${modeConfig.glow} mb-6`}>
                  <span className="text-white scale-150">{modeConfig.icon}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{modeConfig.label} Mode</h3>
                <p className="text-gray-400 text-sm mb-8 max-w-md">{modeConfig.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl w-full">
                  {modeConfig.prompts.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => handleSubmit(prompt)}
                      className="text-left text-sm text-gray-300 bg-gray-800/60 hover:bg-gray-800 border border-gray-700 hover:border-gray-500 px-4 py-3 rounded-xl transition-all group"
                    >
                      <span className="text-gray-500 group-hover:text-gray-400 mr-2">→</span>
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Query Input Bar ── */}
          <div className="border-t border-gray-800 bg-gray-950 p-4">
            <div className="max-w-4xl mx-auto">
              <div className={`flex items-end gap-3 bg-gray-900 border border-gray-700 hover:border-gray-500 focus-within:border-blue-500/50 rounded-2xl px-4 py-3 transition-colors`}>
                <textarea
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Ask ${modeConfig.label} Mode anything about your ${workspace.type === "github" ? "repository" : "project"}...`}
                  rows={1}
                  disabled={isQuerying}
                  className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none text-sm leading-relaxed"
                  style={{ maxHeight: "120px", overflowY: "auto" }}
                  onInput={(e) => {
                    const t = e.target as HTMLTextAreaElement;
                    t.style.height = "auto";
                    t.style.height = Math.min(t.scrollHeight, 120) + "px";
                  }}
                />
                <button
                  onClick={() => handleSubmit()}
                  disabled={!query.trim() || isQuerying}
                  className={`
                    flex items-center justify-center w-9 h-9 rounded-xl transition-all shrink-0
                    ${query.trim() && !isQuerying
                      ? `bg-gradient-to-br ${modeConfig.gradient} text-white shadow-lg hover:opacity-90`
                      : "bg-gray-800 text-gray-600 cursor-not-allowed"}
                  `}
                >
                  {isQuerying ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-600 mt-2 text-center">
                Press <kbd className="bg-gray-800 px-1 rounded">Enter</kbd> to send · <kbd className="bg-gray-800 px-1 rounded">Shift+Enter</kbd> for new line
              </p>
            </div>
          </div>
        </main>

        {/* ── Right: History Panel ── */}
        {showHistory && (
          <aside className="w-72 border-l border-gray-800 bg-gray-950 flex flex-col overflow-hidden shrink-0">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
              <span className="text-sm font-medium text-gray-300">Query History</span>
              <button onClick={() => setShowHistory(false)}>
                <X className="w-4 h-4 text-gray-500 hover:text-white" />
              </button>
            </div>
            <div className="flex-1 overflow-auto divide-y divide-gray-800">
              {history.length === 0 ? (
                <div className="p-6 text-center text-gray-500 text-sm">No history yet</div>
              ) : (
                history.map((item) => {
                  const m = MODES.find((x) => x.id === item.mode)!;
                  return (
                    <button
                      key={item.id}
                      onClick={() => { setCurrentResult(item); setMode(item.mode); setShowHistory(false); }}
                      className="w-full text-left p-4 hover:bg-gray-800/60 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs ${m.color}`}>{m.label}</span>
                        <span className="text-xs text-gray-600">
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-300 line-clamp-2">{item.query}</p>
                    </button>
                  );
                })
              )}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

// Wrap in Suspense for useSearchParams
export default function WorkspacePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    }>
      <WorkspaceContent />
    </Suspense>
  );
}
