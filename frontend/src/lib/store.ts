/**
 * Global state store using Zustand
 */
import { create } from "zustand";

export type AIMode = "illustration" | "development" | "testing" | "deployment" | "documentation";

export interface QueryHistoryItem {
  id: string;
  mode: AIMode;
  query: string;
  result: {
    type: string;
    content: string;
    explanation?: string;
    metadata?: Record<string, any>;
  };
  suggestions?: string[];
  timestamp: Date;
}

export interface WorkspaceInfo {
  workspace_id: string;
  type: "github" | "transcript";
  metadata: {
    repo_name?: string;
    repo_url?: string;
    language?: string;
    description?: string;
    file_count?: number;
    stars?: number;
    requirements?: string[];
    user_stories?: string[];
    tickets?: any[];
  };
  created_at: string;
}

export interface ConversationInfo {
  id: string;
  workspace_id: string;
  title: string | null;
  created_at: string;
  last_updated: string;
  message_count: number;
}

interface DevPilotStore {
  // Workspace
  workspace: WorkspaceInfo | null;
  setWorkspace: (ws: WorkspaceInfo) => void;
  clearWorkspace: () => void;

  // Mode
  currentMode: AIMode;
  setMode: (mode: AIMode) => void;

  // Loading states
  isAnalyzing: boolean;
  setIsAnalyzing: (v: boolean) => void;
  isQuerying: boolean;
  setIsQuerying: (v: boolean) => void;

  // Query history
  history: QueryHistoryItem[];
  addToHistory: (item: QueryHistoryItem) => void;
  clearHistory: () => void;

  // Current result
  currentResult: QueryHistoryItem | null;
  setCurrentResult: (r: QueryHistoryItem | null) => void;

  // Error
  error: string | null;
  setError: (e: string | null) => void;

  // Conversations
  currentConversation: ConversationInfo | null;
  setCurrentConversation: (c: ConversationInfo | null) => void;
  conversations: ConversationInfo[];
  setConversations: (c: ConversationInfo[]) => void;
}

export const useStore = create<DevPilotStore>((set) => ({
  workspace: null,
  setWorkspace: (ws) => set({ workspace: ws }),
  clearWorkspace: () => set({ workspace: null, history: [], currentResult: null }),

  currentMode: "illustration",
  setMode: (mode) => set({ currentMode: mode }),

  isAnalyzing: false,
  setIsAnalyzing: (v) => set({ isAnalyzing: v }),
  isQuerying: false,
  setIsQuerying: (v) => set({ isQuerying: v }),

  history: [],
  addToHistory: (item) =>
    set((state) => ({ history: [item, ...state.history].slice(0, 50) })),
  clearHistory: () => set({ history: [] }),

  currentResult: null,
  setCurrentResult: (r) => set({ currentResult: r }),

  error: null,
  setError: (e) => set({ error: e }),

  currentConversation: null,
  setCurrentConversation: (c) => set({ currentConversation: c }),
  conversations: [],
  setConversations: (c) => set({ conversations: c }),
}));
