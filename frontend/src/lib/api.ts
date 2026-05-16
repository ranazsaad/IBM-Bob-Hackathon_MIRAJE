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
}

// Export singleton instance
export const api = new APIClient();

// Export class for custom instances
export default APIClient;

// Made with Bob
