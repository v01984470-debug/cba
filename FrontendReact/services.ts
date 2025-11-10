import { API_BASE_URL } from "./constants";
import {
  Case,
  ReportData,
  ReportSummary,
  ProcessCasesResponse,
  EmailPreview,
  EmailPreviewResponse,
  CreateCasesResponse,
  PacsPair,
  PacsPairsResponse,
  CreateCaseFromFilesResponse,
  RegenerateEmailResponse,
} from "./types";

class ApiService {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`API Request: ${options?.method || "GET"} ${url}`);

      const response = await fetch(url, {
        ...options,
        headers: {
          ...options?.headers,
        },
      });

      console.log(`API Response: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: response.statusText };
        }
        const errorMessage =
          errorData.message ||
          errorData.error ||
          `HTTP ${response.status}: ${response.statusText}`;
        console.error(`API Error: ${errorMessage}`);
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("API Response data:", data);
      return data;
    } catch (error) {
      console.error("API Request failed:", error);
      if (error instanceof Error) {
        // Check for network errors
        if (
          error.message.includes("Failed to fetch") ||
          error.message.includes("NetworkError")
        ) {
          throw new Error(
            `Unable to connect to server at ${API_BASE_URL}. Please ensure the backend is running.`
          );
        }
        throw new Error(error.message || "An unknown network error occurred.");
      }
      throw new Error("An unknown error occurred.");
    }
  }

  // Case Management
  async getCases(): Promise<Case[]> {
    return this.request<Case[]>("/api/cases");
  }

  async getCaseById(caseId: string): Promise<Case> {
    return this.request<Case>(`/api/cases/${caseId}`);
  }

  async deleteCase(
    caseId: string
  ): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/cases/${caseId}`, { method: "DELETE" });
  }

  async deleteAllCases(): Promise<{ success: boolean; message: string }> {
    return this.request("/api/cases", { method: "DELETE" });
  }

  async processCases(caseIds: string[]): Promise<ProcessCasesResponse> {
    const formData = new FormData();
    caseIds.forEach((id) => formData.append("case_ids", id));
    return this.request<ProcessCasesResponse>("/process-cases", {
      method: "POST",
      body: formData,
    });
  }

  // Report Endpoints
  async getReport(identifier: string): Promise<ReportData> {
    return this.request<ReportData>(`/api/report/${identifier}`);
  }

  async getReports(): Promise<ReportSummary[]> {
    return this.request<ReportSummary[]>("/api/reports");
  }

  // Processing Endpoints
  async uploadPacsPreview(
    pacs004Files: File[],
    pacs008Files: File[]
  ): Promise<EmailPreviewResponse> {
    const formData = new FormData();
    pacs004Files.forEach((file) => formData.append("pacs004_files", file));
    pacs008Files.forEach((file) => formData.append("pacs008_files", file));
    return this.request<EmailPreviewResponse>("/upload-pacs-preview", {
      method: "POST",
      body: formData,
    });
  }

  async createCasesFromEmails(
    selectedIndices: number[],
    emailPreviews: EmailPreview[]
  ): Promise<CreateCasesResponse> {
    const selectedPreviews = emailPreviews.filter((p) =>
      selectedIndices.includes(p.index)
    );
    return this.request<CreateCasesResponse>("/create-cases-from-emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_indices: selectedIndices,
        email_previews: selectedPreviews,
      }),
    });
  }

  // PACS File Pairs
  async getPacsPairs(): Promise<PacsPairsResponse> {
    return this.request<PacsPairsResponse>("/api/pacs-pairs");
  }

  async generateEmailPreviewFromFiles(
    pacs004Path: string,
    pacs008Path: string
  ): Promise<EmailPreviewResponse> {
    return this.request<EmailPreviewResponse>(
      "/api/generate-email-preview-from-files",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pacs004_path: pacs004Path,
          pacs008_path: pacs008Path,
        }),
      }
    );
  }

  async createCaseFromFiles(
    pacs004Path: string,
    pacs008Path: string
  ): Promise<CreateCaseFromFilesResponse> {
    return this.request<CreateCaseFromFilesResponse>(
      "/api/create-case-from-files",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pacs004_path: pacs004Path,
          pacs008_path: pacs008Path,
        }),
      }
    );
  }

  // Regenerate Email
  async regenerateEmail(runId: string): Promise<RegenerateEmailResponse> {
    return this.request<RegenerateEmailResponse>("/api/regenerate-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id: runId }),
    });
  }
}

export const apiService = new ApiService();
