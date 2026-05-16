/**
 * API Client for DevPilot AI Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface GitHubAnalyzeRequest {
  repo_url: string;
  branch?: string;
  depth?: string;
}

export interface TranscriptAnalyzeRequest {
  transcript: string;
  context?: string;
}

export interface ModeQueryRequest {
  workspace_id: string;
  query: string;
  context?: Record<string, any>;
}

export interface WorkspaceResponse {
  workspace_id: string;
  type: string;
  metadata: Record<string, any>;
  created_at: string;
  last_accessed: string;
  file_count?: number;
}

export interface ModeQueryResponse {
  mode: string;
  result: {
    type: string;
    content: string;
    explanation?: string;
    metadata?: Record<string, any>;
  };
  suggestions?: string[];
}

export interface ConversationResponse {
  id: string;
  workspace_id: string;
  title: string | null;
  created_at: string;
  last_updated: string;
  message_count: number;
  messages: MessageResponse[];
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  metadata: Record<string, any> | null;
  timestamp: string;
}

export interface MessageCreate {
  role: string;
  content: string;
  metadata?: Record<string, any>;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Request failed:", error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request("/health");
  }

  // Analyze GitHub repository
  async analyzeGitHub(data: GitHubAnalyzeRequest) {
    return this.request("/analyze/github", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Analyze meeting transcript
  async analyzeTranscript(data: TranscriptAnalyzeRequest) {
    return this.request("/analyze/transcript", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Get workspace details
  async getWorkspace(workspaceId: string): Promise<WorkspaceResponse> {
    return this.request(`/workspace/${workspaceId}`);
  }

  // Get workspace files
  async getWorkspaceFiles(workspaceId: string) {
    return this.request(`/workspace/${workspaceId}/files`);
  }

  // Delete workspace
  async deleteWorkspace(workspaceId: string) {
    return this.request(`/workspace/${workspaceId}`, {
      method: "DELETE",
    });
  }

  // AI Mode Queries
  async queryIllustrationMode(data: ModeQueryRequest): Promise<ModeQueryResponse> {
    return this.request("/modes/illustration/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async queryDevelopmentMode(data: ModeQueryRequest): Promise<ModeQueryResponse> {
    return this.request("/modes/development/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async queryTestingMode(data: ModeQueryRequest): Promise<ModeQueryResponse> {
    return this.request("/modes/testing/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async queryDeploymentMode(data: ModeQueryRequest): Promise<ModeQueryResponse> {
    return this.request("/modes/deployment/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async queryDocumentationMode(data: ModeQueryRequest): Promise<ModeQueryResponse> {
    return this.request("/modes/documentation/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Generic mode query
  async queryMode(mode: string, data: ModeQueryRequest): Promise<ModeQueryResponse> {
    const modeMap: Record<string, (data: ModeQueryRequest) => Promise<ModeQueryResponse>> = {
      illustration: this.queryIllustrationMode.bind(this),
      development: this.queryDevelopmentMode.bind(this),
      testing: this.queryTestingMode.bind(this),
      deployment: this.queryDeploymentMode.bind(this),
      documentation: this.queryDocumentationMode.bind(this),
    };

    const queryFn = modeMap[mode];
    if (!queryFn) {
      throw new Error(`Unknown mode: ${mode}`);
    }

    return queryFn(data);
  }

  // Conversation Management
  async createConversation(workspaceId: string, title?: string): Promise<ConversationResponse> {
    return this.request(`/conversations?workspace_id=${workspaceId}${title ? `&title=${encodeURIComponent(title)}` : ''}`, {
      method: "POST",
    });
  }

  async getConversation(conversationId: string): Promise<ConversationResponse> {
    return this.request(`/conversations/${conversationId}`);
  }

  async listConversations(workspaceId: string): Promise<ConversationResponse[]> {
    return this.request(`/conversations/workspace/${workspaceId}`);
  }

  async addMessage(conversationId: string, message: MessageCreate): Promise<MessageResponse> {
    return this.request(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify(message),
    });
  }

  async deleteConversation(conversationId: string) {
    return this.request(`/conversations/${conversationId}`, {
      method: "DELETE",
    });
  }

  async updateConversationTitle(conversationId: string, title: string) {
    return this.request(`/conversations/${conversationId}/title?title=${encodeURIComponent(title)}`, {
      method: "PATCH",
    });
  }

  // VS Code Integration
  async cloneRepo(repoUrl: string, workspacePath?: string) {
    return this.request("/vscode/clone-repo", {
      method: "POST",
      body: JSON.stringify({ repo_url: repoUrl, workspace_path: workspacePath }),
    });
  }

  async openFile(filePath: string, workspacePath?: string, lineNumber?: number) {
    return this.request("/vscode/open-file", {
      method: "POST",
      body: JSON.stringify({ file_path: filePath, workspace_path: workspacePath, line_number: lineNumber }),
    });
  }

  async openWorkspace(workspaceId: string) {
    return this.request(`/vscode/open-workspace?workspace_id=${workspaceId}`, {
      method: "POST",
    });
  }

  async listWorkspaceFiles(workspacePath: string) {
    return this.request(`/vscode/workspace-files?workspace_path=${encodeURIComponent(workspacePath)}`);
  }

  async checkVSCode() {
    return this.request("/vscode/check-vscode");
  }
}

// Export singleton instance
export const api = new APIClient();

// Export class for custom instances
export default APIClient;

// Made with Bob
