import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "../components/Toast";
import { apiService } from "../services";
import { Case, PacsPair, EmailPreview } from "../types";

// Smaller components defined within the Dashboard file for cohesiveness

const Spinner: React.FC = () => (
  <svg
    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    ></circle>
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
  </svg>
);

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  variant?: "primary" | "secondary" | "danger";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { children, isLoading, disabled, variant = "primary", className, ...props },
    ref
  ) => {
    const baseClasses =
      "inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors";
    const variantClasses = {
      primary:
        "text-white bg-gray-800 hover:bg-gray-700 focus:ring-gray-500 dark:bg-yellow-500 dark:hover:bg-yellow-600 dark:text-black dark:focus:ring-yellow-400",
      secondary:
        "text-gray-700 bg-gray-200 hover:bg-gray-300 focus:ring-gray-400 dark:text-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-500",
      danger: "text-white bg-red-600 hover:bg-red-700 focus:ring-red-500",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseClasses} ${variantClasses[variant]} ${className}`}
        {...props}
      >
        {isLoading && <Spinner />}
        {children}
      </button>
    );
  }
);

const Dashboard: React.FC = () => {
  const [mode, setMode] = useState<"manual" | "automated">("manual");
  const [cases, setCases] = useState<Case[]>([]);
  const [isLoadingCases, setIsLoadingCases] = useState(true);
  const [selectedCaseIds, setSelectedCaseIds] = useState<string[]>([]);

  const [pacsPairs, setPacsPairs] = useState<PacsPair[]>([]);
  const [isLoadingPairs, setIsLoadingPairs] = useState(false);
  const [selectedPairId, setSelectedPairId] = useState<string | null>(null);
  const [selectedPair, setSelectedPair] = useState<PacsPair | null>(null);
  const [emailPreviews, setEmailPreviews] = useState<EmailPreview[]>([]);
  const [selectedEmailIndices, setSelectedEmailIndices] = useState<number[]>(
    []
  );
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);
  const [isCreatingCases, setIsCreatingCases] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedCaseForView, setSelectedCaseForView] = useState<Case | null>(
    null
  );
  const [showCaseModal, setShowCaseModal] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  // Use a ref to track cases for the interval without causing re-renders
  const casesRef = React.useRef<Case[]>([]);

  const fetchCases = useCallback(async () => {
    try {
      const fetchedCases = await apiService.getCases();
      const sortedCases = fetchedCases.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setCases(sortedCases);
      casesRef.current = sortedCases; // Update ref with latest cases
    } catch (error) {
      toast(
        error instanceof Error ? error.message : "Failed to fetch cases",
        "error"
      );
    } finally {
      setIsLoadingCases(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchCases();
    const interval = setInterval(() => {
      // Check if any cases are processing using the ref (no state update needed)
      const hasProcessing = casesRef.current.some(
        (c) => c.status === "processing"
      );
      if (hasProcessing) {
        fetchCases();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchCases]);

  const fetchPacsPairs = useCallback(async () => {
    setIsLoadingPairs(true);
    try {
      const response = await apiService.getPacsPairs();
      setPacsPairs(response.pairs);
    } catch (error) {
      toast(
        error instanceof Error ? error.message : "Failed to fetch PACS pairs",
        "error"
      );
    } finally {
      setIsLoadingPairs(false);
    }
  }, [toast]);

  useEffect(() => {
    if (mode === "manual") {
      fetchPacsPairs();
    }
  }, [mode, fetchPacsPairs]);

  const handleModeChange = (newMode: "manual" | "automated") => {
    setMode(newMode);
    setSelectedCaseIds([]);
    setSelectedPairId(null);
    setSelectedPair(null);
    setEmailPreviews([]);
    setSelectedEmailIndices([]);
  };

  const handlePairSelection = (pair: PacsPair) => {
    setSelectedPairId(pair.id);
    setSelectedPair(pair);
    // Clear previous email previews when selecting a new pair
    setEmailPreviews([]);
    setSelectedEmailIndices([]);
  };

  const handleGenerateEmail = async () => {
    if (!selectedPair) {
      toast("Please select a PACS file pair first.", "info");
      return;
    }

    setIsGeneratingEmail(true);
    try {
      const response = await apiService.generateEmailPreviewFromFiles(
        selectedPair.pacs004_path,
        selectedPair.pacs008_path
      );

      if (response.success && response.email_previews) {
        setEmailPreviews(response.email_previews);
        toast(
          `Generated ${response.email_previews.length} email preview(s).`,
          "success"
        );
      } else {
        toast(response.message, "error");
      }
    } catch (error) {
      toast(
        error instanceof Error
          ? error.message
          : "Failed to generate email preview.",
        "error"
      );
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  const handleCreateCases = async () => {
    if (selectedEmailIndices.length === 0) {
      toast("Please select email previews to create cases from.", "info");
      return;
    }

    if (!selectedPair) {
      toast("No PACS pair selected.", "error");
      return;
    }

    setIsCreatingCases(true);
    try {
      // Create cases from selected email previews
      const selectedPreviews = emailPreviews.filter((p) =>
        selectedEmailIndices.includes(p.index)
      );

      const createdCases: Case[] = [];
      for (const preview of selectedPreviews) {
        try {
          const response = await apiService.createCaseFromFiles(
            selectedPair.pacs004_path,
            selectedPair.pacs008_path
          );

          if (response.success && response.case) {
            createdCases.push(response.case);
          } else if (response.is_duplicate) {
            toast(
              `Duplicate case detected. Existing case: ${response.existing_case_id}`,
              "info"
            );
          }
        } catch (error) {
          toast(
            error instanceof Error ? error.message : "Failed to create case.",
            "error"
          );
        }
      }

      if (createdCases.length > 0) {
        toast(
          `Successfully created ${createdCases.length} case(s).`,
          "success"
        );
        setEmailPreviews([]);
        setSelectedEmailIndices([]);
        setSelectedPairId(null);
        setSelectedPair(null);
        fetchCases();
      }
    } catch (error) {
      toast(
        error instanceof Error ? error.message : "Failed to create cases.",
        "error"
      );
    } finally {
      setIsCreatingCases(false);
    }
  };

  const handleProcessCases = async () => {
    if (selectedCaseIds.length === 0) {
      toast("Please select a case to process.", "info");
      return;
    }

    // Immediately update status to "processing" for selected cases
    setCases((prevCases) =>
      prevCases.map((c) =>
        selectedCaseIds.includes(c.case_id)
          ? { ...c, status: "processing" as Case["status"] }
          : c
      )
    );
    // Also update the ref
    casesRef.current = casesRef.current.map((c) =>
      selectedCaseIds.includes(c.case_id)
        ? { ...c, status: "processing" as Case["status"] }
        : c
    );

    setIsProcessing(true);
    try {
      const response = await apiService.processCases(selectedCaseIds);
      if (response.success) {
        toast(response.message, "success");
        // Fetch cases to get updated status from backend
        await fetchCases();
        setSelectedCaseIds([]);
        // Stay on dashboard - user can click "View Report" to see the report
      } else {
        // Revert status on error
        await fetchCases();
        toast(response.message, "error");
      }
    } catch (error) {
      // Revert status on error
      await fetchCases();
      toast(
        error instanceof Error ? error.message : "Failed to process cases.",
        "error"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteCase = async (caseId: string) => {
    if (window.confirm(`Are you sure you want to delete case ${caseId}?`)) {
      try {
        const response = await apiService.deleteCase(caseId);
        if (response.success) {
          toast(response.message, "success");
          fetchCases();
        } else {
          toast(response.message, "error");
        }
      } catch (error) {
        toast(
          error instanceof Error ? error.message : "Failed to delete case.",
          "error"
        );
      }
    }
  };

  const handleDeleteAllCases = async () => {
    if (cases.length === 0) {
      toast("No cases to delete.", "info");
      return;
    }

    const confirmMessage = `Are you sure you want to delete ALL ${cases.length} case(s)?\n\nThis action cannot be undone.`;
    if (window.confirm(confirmMessage)) {
      try {
        const response = await apiService.deleteAllCases();
        if (response.success) {
          toast(response.message, "success");
          setSelectedCaseIds([]);
          fetchCases();
        } else {
          toast(response.message, "error");
        }
      } catch (error) {
        toast(
          error instanceof Error
            ? error.message
            : "Failed to delete all cases.",
          "error"
        );
      }
    }
  };

  const handleViewCase = async (caseId: string) => {
    try {
      const caseData = await apiService.getCaseById(caseId);
      setSelectedCaseForView(caseData);
      setShowCaseModal(true);
    } catch (error) {
      toast(
        error instanceof Error ? error.message : "Failed to load case details.",
        "error"
      );
    }
  };

  const handleOpenCaseReport = (caseId: string) => {
    const caseData = cases.find((c) => c.case_id === caseId);
    if (caseData && caseData.run_id) {
      window.open(`#/report/${caseData.run_id}`, "_blank");
    } else {
      toast(
        "This case has not been processed yet. Please process the case first to view the report.",
        "info"
      );
    }
  };

  const formatAmount = (amount: string, emailBody?: string): string => {
    if (!amount || amount === "0" || amount === "0.00" || amount === "") {
      if (emailBody) {
        const amountMatch = emailBody.match(/:32A:\d{6}(\w{3})(\d+\.?\d*)/);
        if (amountMatch) {
          const extractedAmount = parseFloat(amountMatch[2]);
          if (!isNaN(extractedAmount) && extractedAmount > 0) {
            return extractedAmount.toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });
          }
        }
      }
      return "N/A";
    }
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount === 0) {
      return "N/A";
    }
    return numAmount.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  return (
    <div className="space-y-8">
      <ModeAndUploadSection
        mode={mode}
        onModeChange={handleModeChange}
        pacsPairs={pacsPairs}
        isLoadingPairs={isLoadingPairs}
        selectedPairId={selectedPairId}
        onPairSelection={handlePairSelection}
        onGenerateEmail={handleGenerateEmail}
        isGeneratingEmail={isGeneratingEmail}
      />
      {emailPreviews.length > 0 && mode === "manual" && (
        <EmailPreviewSection
          previews={emailPreviews}
          selectedIndices={selectedEmailIndices}
          onSelectionChange={setSelectedEmailIndices}
          onCreateCases={handleCreateCases}
          isCreatingCases={isCreatingCases}
        />
      )}
      <CaseManagementSection
        cases={cases}
        isLoading={isLoadingCases}
        mode={mode}
        selectedCaseIds={selectedCaseIds}
        onSelectionChange={setSelectedCaseIds}
        onProcess={handleProcessCases}
        isProcessing={isProcessing}
        onDeleteCase={handleDeleteCase}
        onDeleteAllCases={handleDeleteAllCases}
        onViewCase={handleViewCase}
        onOpenCaseReport={handleOpenCaseReport}
        formatAmount={formatAmount}
      />
      {showCaseModal && selectedCaseForView && (
        <CaseViewModal
          caseData={selectedCaseForView}
          onClose={() => {
            setShowCaseModal(false);
            setSelectedCaseForView(null);
          }}
          onProcess={() => {
            setShowCaseModal(false);
            setSelectedCaseForView(null);
            handleProcessCases();
          }}
        />
      )}
    </div>
  );
};

// Sub-components for Dashboard
const ModeAndUploadSection: React.FC<{
  mode: "manual" | "automated";
  onModeChange: (mode: "manual" | "automated") => void;
  pacsPairs: PacsPair[];
  isLoadingPairs: boolean;
  selectedPairId: string | null;
  onPairSelection: (pair: PacsPair) => void;
  onGenerateEmail: () => void;
  isGeneratingEmail: boolean;
}> = ({
  mode,
  onModeChange,
  pacsPairs,
  isLoadingPairs,
  selectedPairId,
  onPairSelection,
  onGenerateEmail,
  isGeneratingEmail,
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Manage and process refund investigation cases.
          </p>
        </div>
        <div className="flex items-center gap-2 p-1 rounded-lg bg-gray-200 dark:bg-gray-700">
          <button
            onClick={() => onModeChange("manual")}
            className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${
              mode === "manual"
                ? "bg-white dark:bg-gray-900 text-yellow-600"
                : "text-gray-600 dark:text-gray-300"
            }`}
          >
            Sequential
          </button>
          <button
            onClick={() => onModeChange("automated")}
            className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${
              mode === "automated"
                ? "bg-white dark:bg-gray-900 text-yellow-600"
                : "text-gray-600 dark:text-gray-300"
            }`}
          >
            Bulk
          </button>
        </div>
      </div>
      {mode === "manual" && (
        <div className="mt-6 border-t border-gray-200 dark:border-gray-700 pt-6">
          <h3 className="text-lg font-semibold mb-4">Select PACS File Pair</h3>
          {isLoadingPairs ? (
            <div className="text-center py-8">
              <Spinner />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Loading available PACS pairs...
              </p>
            </div>
          ) : pacsPairs.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">
                No PACS file pairs found in samples directory.
              </p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto pr-2">
              {pacsPairs.map((pair) => (
                <div
                  key={pair.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedPairId === pair.id
                      ? "border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 ring-2 ring-yellow-500"
                      : isGeneratingEmail
                      ? "border-gray-200 dark:border-gray-700 opacity-50 cursor-not-allowed"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                  onClick={() => !isGeneratingEmail && onPairSelection(pair)}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <div className="text-sm space-y-1">
                        <p className="truncate" title={pair.pacs004_filename}>
                          📄 {pair.pacs004_filename}
                        </p>
                        <p className="truncate" title={pair.pacs008_filename}>
                          📄 {pair.pacs008_filename}
                        </p>
                      </div>
                      {selectedPairId === pair.id && isGeneratingEmail && (
                        <div className="mt-3 flex items-center gap-2 text-xs text-yellow-600 dark:text-yellow-400">
                          <Spinner />
                          <span>Generating email...</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {selectedPairId && (
            <div className="mt-6 text-right">
              <Button onClick={onGenerateEmail} isLoading={isGeneratingEmail}>
                Initiate Case with Return Message
              </Button>
            </div>
          )}
          <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
            Select a PACS file pair, then click "Initiate Case with Return
            Message" to see the generated email from logger agent.
          </p>
        </div>
      )}
    </div>
  );
};

const EmailPreviewSection: React.FC<{
  previews: EmailPreview[];
  selectedIndices: number[];
  onSelectionChange: (indices: number[]) => void;
  onCreateCases: () => void;
  isCreatingCases: boolean;
}> = ({
  previews,
  selectedIndices,
  onSelectionChange,
  onCreateCases,
  isCreatingCases,
}) => {
  const handleSelectAll = (checked: boolean) => {
    onSelectionChange(checked ? previews.map((p) => p.index) : []);
  };
  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4">Email Previews</h3>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-gray-300 text-yellow-600 focus:ring-yellow-500"
            onChange={(e) => handleSelectAll(e.target.checked)}
            checked={
              previews.length > 0 && selectedIndices.length === previews.length
            }
          />
          <label className="text-sm">Select All</label>
        </div>
        <Button
          onClick={onCreateCases}
          isLoading={isCreatingCases}
          disabled={selectedIndices.length === 0}
        >
          Create {selectedIndices.length} Selected Case(s)
        </Button>
      </div>
      <div className="space-y-4">
        {previews.map((preview) => (
          <div
            key={preview.index}
            className={`border rounded-lg p-6 transition-all ${
              selectedIndices.includes(preview.index)
                ? "border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 ring-2 ring-yellow-500"
                : "border-gray-200 dark:border-gray-700"
            }`}
          >
            <div className="flex items-start gap-4 mb-4">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-yellow-600 focus:ring-yellow-500 mt-1"
                checked={selectedIndices.includes(preview.index)}
                onChange={() => {
                  const newSelection = selectedIndices.includes(preview.index)
                    ? selectedIndices.filter((i) => i !== preview.index)
                    : [...selectedIndices, preview.index];
                  onSelectionChange(newSelection);
                }}
              />
              <div className="flex-1">
                <div className="mb-4">
                  <p className="font-semibold text-sm mb-1">
                    {preview.debtor_name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {preview.amount} {preview.currency}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="mb-2">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                      From:
                    </p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      CBA Refund System &lt;refunds@cba.com.au&gt;
                    </p>
                  </div>
                  <div className="mb-2">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                      To:
                    </p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {preview.email_recipient}
                    </p>
                  </div>
                  <div className="mb-2">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                      Subject:
                    </p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {preview.email_subject}
                    </p>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      Message:
                    </p>
                    <pre className="text-xs font-mono text-gray-900 dark:text-white whitespace-pre-wrap overflow-x-auto bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
                      {preview.email_body}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const CaseManagementSection: React.FC<{
  cases: Case[];
  isLoading: boolean;
  mode: "manual" | "automated";
  selectedCaseIds: string[];
  onSelectionChange: (ids: string[]) => void;
  onProcess: () => void;
  isProcessing: boolean;
  onDeleteCase: (caseId: string) => void;
  onDeleteAllCases: () => void;
  onViewCase: (caseId: string) => void;
  onOpenCaseReport: (caseId: string) => void;
  formatAmount: (amount: string, emailBody?: string) => string;
}> = ({
  cases,
  isLoading,
  mode,
  selectedCaseIds,
  onSelectionChange,
  onProcess,
  isProcessing,
  onDeleteCase,
  onDeleteAllCases,
  onViewCase,
  onOpenCaseReport,
  formatAmount,
}) => {
  const StatusBadge: React.FC<{ status: Case["status"] }> = ({ status }) => {
    const styles = {
      generated:
        "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
      processing:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300 animate-pulse",
      completed:
        "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
      failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
    };
    const icons = {
      generated: "📋",
      processing: "⚙️",
      completed: "✅",
      failed: "❌",
    };
    return (
      <span
        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${styles[status]}`}
      >
        {icons[status]} {status}
      </span>
    );
  };

  const handleSelect = (caseId: string) => {
    if (mode === "manual") {
      onSelectionChange([caseId]);
    } else {
      const newSelection = selectedCaseIds.includes(caseId)
        ? selectedCaseIds.filter((id) => id !== caseId)
        : [...selectedCaseIds, caseId];
      onSelectionChange(newSelection);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    onSelectionChange(checked ? cases.map((c) => c.case_id) : []);
  };

  const sortedCases = useMemo(() => cases, [cases]);

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Case Management</h3>
        <div className="flex items-center gap-2">
          <Button
            onClick={onProcess}
            isLoading={isProcessing}
            disabled={selectedCaseIds.length === 0}
          >
            Process Selected
          </Button>
          {cases.length > 0 && (
            <Button
              onClick={onDeleteAllCases}
              variant="danger"
              disabled={isProcessing}
            >
              🗑️ Delete All
            </Button>
          )}
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th scope="col" className="px-6 py-3 text-left">
                {mode === "automated" && (
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-yellow-600 focus:ring-yellow-500"
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    checked={
                      cases.length > 0 &&
                      selectedCaseIds.length === cases.length
                    }
                  />
                )}
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Case ID
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Description
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Amount
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Created
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="text-center py-8">
                  Loading cases...
                </td>
              </tr>
            ) : sortedCases.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8">
                  No cases found.
                </td>
              </tr>
            ) : (
              sortedCases.map((caseItem) => (
                <tr
                  key={caseItem.case_id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700/50"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type={mode === "manual" ? "radio" : "checkbox"}
                      name="case_selection"
                      className="h-4 w-4 rounded border-gray-300 text-yellow-600 focus:ring-yellow-500"
                      checked={selectedCaseIds.includes(caseItem.case_id)}
                      onChange={() => handleSelect(caseItem.case_id)}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      onClick={() => onOpenCaseReport(caseItem.case_id)}
                      className={`font-mono cursor-pointer ${
                        caseItem.status === "completed" && caseItem.run_id
                          ? "text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-bold"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                      title={
                        caseItem.status === "completed" && caseItem.run_id
                          ? "Click to view report in new tab"
                          : "Case not processed yet - process first to view report"
                      }
                    >
                      {caseItem.case_id}{" "}
                      {caseItem.status === "completed" && caseItem.run_id
                        ? "📊"
                        : ""}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {caseItem.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {formatAmount(caseItem.amount, caseItem.email_body)}{" "}
                    {caseItem.currency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <StatusBadge status={caseItem.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {new Date(caseItem.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => onOpenCaseReport(caseItem.case_id)}
                      disabled={
                        !(caseItem.status === "completed" && caseItem.run_id)
                      }
                      className={`px-3 py-1 rounded-md ${
                        caseItem.status === "completed" && caseItem.run_id
                          ? "text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 bg-blue-50 dark:bg-blue-900/20 cursor-pointer"
                          : "text-gray-400 dark:text-gray-600 bg-gray-100 dark:bg-gray-700 cursor-not-allowed opacity-50"
                      }`}
                      title={
                        caseItem.status === "completed" && caseItem.run_id
                          ? "Click to view report in new tab"
                          : "Case not processed yet - process first to view report"
                      }
                    >
                      📊 View Report
                    </button>
                    <button
                      onClick={() => onViewCase(caseItem.case_id)}
                      className="text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300"
                    >
                      👁️ View
                    </button>
                    <button
                      onClick={() => onDeleteCase(caseItem.case_id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const CaseViewModal: React.FC<{
  caseData: Case;
  onClose: () => void;
  onProcess: () => void;
}> = ({ caseData, onClose, onProcess }) => {
  const emailData = caseData as any;
  const emailSubject =
    emailData.email_subject ||
    emailData.email_data?.email_subject ||
    "return of funds";
  const emailRecipient =
    emailData.email_recipient ||
    emailData.email_data?.email_recipient ||
    "Intelli Processing";
  const emailBody =
    emailData.email_body ||
    emailData.email_data?.email_body ||
    "Email content not available";

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          aria-hidden="true"
        ></div>
        <div
          className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="bg-black text-yellow-500 px-6 py-4 flex justify-between items-center">
            <h3 className="text-xl font-semibold">📧 Email Details</h3>
            <button
              onClick={onClose}
              className="text-yellow-500 hover:text-yellow-300 text-2xl"
            >
              &times;
            </button>
          </div>
          <div className="bg-white dark:bg-gray-800 px-6 py-4">
            <div className="space-y-4">
              <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                <div className="flex items-center mb-2">
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 w-20">
                    From:
                  </span>
                  <span className="text-sm text-gray-900 dark:text-white">
                    CBA Refund System &lt;refunds@cba.com.au&gt;
                  </span>
                </div>
                <div className="flex items-center mb-2">
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 w-20">
                    To:
                  </span>
                  <span className="text-sm text-gray-900 dark:text-white">
                    {emailRecipient}
                  </span>
                </div>
                <div className="flex items-center mb-2">
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 w-20">
                    Subject:
                  </span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    {emailSubject}
                  </span>
                </div>
                <div className="flex items-center mb-2">
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 w-20">
                    Date:
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(caseData.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 w-20">
                    Reference:
                  </span>
                  <span className="text-sm font-mono text-red-600 dark:text-red-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    {caseData.case_id}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  MT103 Message:
                </div>
                <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-4">
                  <pre className="text-xs font-mono text-gray-900 dark:text-white whitespace-pre-wrap overflow-x-auto max-h-96">
                    {emailBody}
                  </pre>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Ready to Send
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={onProcess}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium"
              >
                🚀 Process Case
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 rounded-md text-sm font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
