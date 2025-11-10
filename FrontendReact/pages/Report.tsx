import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { apiService } from "../services";
import { ReportData } from "../types";

// Helper components defined within Report.tsx

const Card: React.FC<{
  children: React.ReactNode;
  className?: string;
  title?: string;
}> = ({ children, className, title }) => (
  <div
    className={`bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 ${className}`}
  >
    {title && (
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
        {title}
      </h3>
    )}
    {children}
  </div>
);

const InfoItem: React.FC<{
  label: string;
  value?: string | number | boolean | null;
  isBadge?: boolean;
  badgeType?: "success" | "danger" | "warning" | "info";
}> = ({ label, value, isBadge, badgeType }) => {
  const renderValue = () => {
    if (value === null || typeof value === "undefined")
      return <span className="text-gray-500">N/A</span>;
    if (typeof value === "boolean") return value ? "Yes" : "No";
    return value;
  };

  const badgeColors = {
    success:
      "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    danger: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
    warning:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
    info: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  };

  if (isBadge && badgeType) {
    return (
      <div className="flex justify-between items-center py-2">
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {label}
        </span>
        <span
          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${badgeColors[badgeType]}`}
        >
          {renderValue()}
        </span>
      </div>
    );
  }

  return (
    <div className="flex justify-between items-center py-2">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <span className="text-sm font-semibold text-gray-900 dark:text-white text-right">
        {renderValue()}
      </span>
    </div>
  );
};

const Report: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<number>(6);

  useEffect(() => {
    if (!runId) {
      setError("No run ID provided in URL");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    apiService
      .getReport(runId)
      .then((data) => {
        console.log("Report data loaded:", data);
        setReportData(data);
        setError(null);
      })
      .catch((err) => {
        console.error("Error loading report:", err);
        setError(err.message || "Failed to load report.");
        setReportData(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [runId]);

  if (isLoading) {
    return (
      <div className="text-center p-8 bg-white dark:bg-gray-800">
        <div className="text-gray-900 dark:text-white">Loading report...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 bg-white dark:bg-gray-800 min-h-screen">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Investigation Report
          </h1>
          <Link
            to="/"
            className="text-yellow-500 hover:text-yellow-600 font-semibold"
          >
            &larr; Back to Dashboard
          </Link>
        </div>
        <div className="text-center p-8 text-red-500 dark:text-red-400">
          <h2 className="text-xl font-semibold mb-2">Error Loading Report</h2>
          <p>Error: {error}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Run ID: {runId}
          </p>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="space-y-6 bg-white dark:bg-gray-800 min-h-screen">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Investigation Report
          </h1>
          <Link
            to="/"
            className="text-yellow-500 hover:text-yellow-600 font-semibold"
          >
            &larr; Back to Dashboard
          </Link>
        </div>
        <div className="text-center p-8 text-gray-500 dark:text-gray-400">
          <h2 className="text-xl font-semibold mb-2">
            No Report Data Available
          </h2>
          <p className="text-sm">Run ID: {runId}</p>
        </div>
      </div>
    );
  }

  const steps = [
    "Case Investigation Starts",
    "Investigator Agent",
    "Actioning Agent",
    "Verifier Agent",
    "Communications Agent",
    "Investigation Report",
    "Case Final Status",
  ];

  return (
    <div className="space-y-6 bg-white dark:bg-gray-800 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Investigation Report
        </h1>
        <Link
          to="/"
          className="text-yellow-500 hover:text-yellow-600 font-semibold"
        >
          &larr; Back to Dashboard
        </Link>
      </div>
      <p className="text-gray-500 dark:text-gray-400">
        Case ID:{" "}
        {reportData?.prep_logger?.case_id ||
          reportData?.case_id ||
          reportData?.transaction_id ||
          runId}
      </p>

      <ReportProgressBar
        steps={steps}
        activeStep={activeStep}
        onStepClick={setActiveStep}
      />

      <div className="mt-6">
        <StepContent step={activeStep} reportData={reportData} />
      </div>
    </div>
  );
};

const ReportProgressBar: React.FC<{
  steps: string[];
  activeStep: number;
  onStepClick: (step: number) => void;
}> = ({ steps, activeStep, onStepClick }) => (
  <div className="w-full">
    <div className="flex justify-between">
      {steps.map((label, index) => {
        const step = index + 1;
        const isActive = step === activeStep;
        const isCompleted = step < activeStep;
        return (
          <div
            key={step}
            className="flex-1 flex items-center cursor-pointer group"
            onClick={() => onStepClick(step)}
          >
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                  isActive
                    ? "bg-yellow-500 text-white"
                    : isCompleted
                    ? "bg-green-500 text-white"
                    : "bg-gray-300 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                }`}
              >
                {isCompleted ? "✓" : step}
              </div>
              <p
                className={`text-xs mt-2 text-center transition-colors ${
                  isActive
                    ? "text-yellow-600 dark:text-yellow-400 font-semibold"
                    : "text-gray-500 dark:text-gray-400"
                }`}
              >
                {label}
              </p>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`flex-auto border-t-2 transition-colors ${
                  isCompleted
                    ? "border-green-500"
                    : "border-gray-300 dark:border-gray-700"
                }`}
              ></div>
            )}
          </div>
        );
      })}
    </div>
  </div>
);

const StepContent: React.FC<{ step: number; reportData: ReportData }> = ({
  step,
  reportData,
}) => {
  try {
    switch (step) {
      case 1: // Case Investigation Starts
        return (
          <Card title="Step 1: Case Investigation Starts (Logger Agent)">
            <InfoItem
              label="Case ID"
              value={
                reportData?.prep_logger?.case_id ||
                reportData?.case_id ||
                reportData?.transaction_id
              }
            />
            <InfoItem label="UETR" value={reportData?.uetr} />
            <InfoItem
              label="End-to-End ID"
              value={reportData?.transaction_id}
            />
            <InfoItem
              label="Email Subject"
              value={
                reportData?.prep_logger?.email_payload?.subject ||
                reportData?.communications?.email_payload?.subject
              }
            />
            <InfoItem
              label="Email Reference"
              value={reportData?.prep_logger?.email_payload?.reference}
            />
            <InfoItem
              label="Email Recipient"
              value={
                reportData?.prep_logger?.email_recipient ||
                reportData?.communications?.email_recipient ||
                "Intelli Processing"
              }
            />
            <InfoItem
              label="Processing Time"
              value={
                reportData?.prep_logger?.processing_timestamp
                  ? new Date(
                      reportData.prep_logger.processing_timestamp
                    ).toLocaleString()
                  : reportData?.timestamp
                  ? new Date(reportData.timestamp).toLocaleString()
                  : "N/A"
              }
            />
            {(reportData?.prep_logger?.email_payload?.body ||
              reportData?.communications?.email_payload?.body) && (
              <div className="mt-4">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  MT103 Message:
                </div>
                <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-4">
                  <pre className="text-xs font-mono text-gray-900 dark:text-white whitespace-pre-wrap overflow-x-auto max-h-96">
                    {reportData?.prep_logger?.email_payload?.body ||
                      reportData?.communications?.email_payload?.body ||
                      ""}
                  </pre>
                </div>
              </div>
            )}
          </Card>
        );
      case 2: // Investigator Agent
        const eligibility = reportData?.investigation?.eligibility || {};
        const csvValidation = reportData?.investigation?.csv_validation || {};
        const p004 = reportData?.parsed_data?.pacs004 || {};
        const p008 = reportData?.parsed_data?.pacs008 || {};
        return (
          <Card title="Step 2: Investigator Agent">
            <div className="grid md:grid-cols-2 gap-x-8 gap-y-2">
              <InfoItem label="UETR" value={p004?.uetr || reportData?.uetr} />
              <InfoItem
                label="E2E ID"
                value={p004?.e2e || reportData?.transaction_id}
              />
              <InfoItem
                label="Customer IBAN"
                value={p004?.cdtr_iban || p008?.dbtr_iban}
              />
              <InfoItem
                label="Return Reason"
                value={
                  eligibility?.reason && eligibility?.reason_info
                    ? `${eligibility.reason} - ${eligibility.reason_info}`
                    : eligibility?.reason || eligibility?.reason_info || "N/A"
                }
              />
              <InfoItem
                label="Auto Refund Eligible"
                value={eligibility?.eligible_auto_refund}
              />
              <InfoItem label="Customer Valid" value={csvValidation?.ok} />
              <InfoItem
                label="Cross Checks"
                value={
                  reportData?.investigation?.cross_errors?.length === 0
                    ? "Passed"
                    : `Failed (${
                        reportData?.investigation?.cross_errors?.length || 0
                      } errors)`
                }
              />
              <InfoItem
                label="Currency Mismatch"
                value={eligibility?.currency_mismatch}
              />
              <InfoItem
                label="Is AUD Refund"
                value={eligibility?.is_aud_refund}
              />
              <InfoItem
                label="FX Loss (AUD)"
                value={
                  eligibility?.fx_loss_aud != null
                    ? `AUD ${eligibility.fx_loss_aud.toFixed(2)}`
                    : "N/A"
                }
              />
              <InfoItem
                label="FX Loss Within Limit"
                value={eligibility?.fx_loss_within_limit}
              />
              <InfoItem label="Non Branch" value={eligibility?.non_branch} />
              <InfoItem
                label="Sanctions OK"
                value={eligibility?.sanctions_ok}
              />
              <InfoItem
                label="Original Amount"
                value={
                  eligibility?.original_amount != null
                    ? `${eligibility.original_amount} ${
                        eligibility.original_currency || ""
                      }`
                    : "N/A"
                }
              />
              <InfoItem
                label="Returned Amount"
                value={
                  eligibility?.returned_amount != null
                    ? `${eligibility.returned_amount} ${
                        eligibility.returned_currency || ""
                      }`
                    : "N/A"
                }
              />
            </div>
          </Card>
        );
      case 3: {
        // Actioning Agent
        const fxCalc = reportData?.fx_calculation || reportData?.fx || {};
        const verifierSummary =
          reportData?.verification?.verifier_summary || {};
        const verifierChecks = verifierSummary?.checks || {};
        const nostroResult =
          verifierSummary?.nostro_result ||
          reportData?.verification?.nostro_result ||
          verifierChecks?.nostro_result ||
          {};
        const checklist =
          reportData?.flow_checklist?.checks ||
          reportData?.flow_checklist ||
          {};

        return (
          <Card title="Step 3: Actioning Agent">
            <div className="grid md:grid-cols-2 gap-x-8 gap-y-2">
              <InfoItem
                label="FX Loss AUD"
                value={
                  fxCalc?.loss_aud !== undefined
                    ? `$${fxCalc.loss_aud}`
                    : fxCalc?.fx_loss_aud !== undefined
                    ? `$${fxCalc.fx_loss_aud}`
                    : "N/A"
                }
              />
              <InfoItem
                label="Exceeds $300"
                value={
                  fxCalc?.exceeds_limit !== undefined
                    ? fxCalc.exceeds_limit
                      ? "Yes"
                      : "No"
                    : fxCalc?.exceeds_300 !== undefined
                    ? fxCalc.exceeds_300
                      ? "Yes"
                      : "No"
                    : "N/A"
                }
              />
              <InfoItem
                label="FCA Account Found"
                value={
                  fxCalc?.fca_account_found !== undefined
                    ? fxCalc.fca_account_found
                      ? "Yes"
                      : "No"
                    : "N/A"
                }
              />
              <InfoItem
                label="Nostro Match"
                value={
                  nostroResult?.found !== undefined
                    ? nostroResult.found
                      ? "Yes"
                      : "No"
                    : verifierChecks?.nostro_match_found !== undefined
                    ? verifierChecks.nostro_match_found
                      ? "Yes"
                      : "No"
                    : "N/A"
                }
              />
              <InfoItem
                label="Manual Review Required"
                value={
                  reportData?.flow_checklist?.manual_review_required !==
                  undefined
                    ? reportData.flow_checklist.manual_review_required
                      ? "Yes"
                      : "No"
                    : checklist?.manual_review_required !== undefined
                    ? checklist.manual_review_required
                      ? "Yes"
                      : "No"
                    : "N/A"
                }
              />
              <InfoItem
                label="Original Amount"
                value={
                  fxCalc?.original_amount || fxCalc?.original_amount_aud
                    ? `${
                        fxCalc?.original_amount || fxCalc?.original_amount_aud
                      } ${fxCalc?.original_currency || ""}`
                    : "N/A"
                }
              />
              <InfoItem
                label="Returned Amount"
                value={
                  fxCalc?.returned_amount || fxCalc?.returned_amount_aud
                    ? `${
                        fxCalc?.returned_amount || fxCalc?.returned_amount_aud
                      } ${fxCalc?.returned_currency || ""}`
                    : "N/A"
                }
              />
              <InfoItem
                label="Original AUD"
                value={
                  fxCalc?.original_amount_aud !== undefined
                    ? `$${fxCalc.original_amount_aud}`
                    : fxCalc?.original_aud !== undefined
                    ? `$${fxCalc.original_aud}`
                    : "N/A"
                }
              />
              <InfoItem
                label="Returned AUD"
                value={
                  fxCalc?.returned_amount_aud !== undefined
                    ? `$${fxCalc.returned_amount_aud}`
                    : fxCalc?.returned_aud !== undefined
                    ? `$${fxCalc.returned_aud}`
                    : "N/A"
                }
              />
            </div>
          </Card>
        );
      }
      case 4: {
        // Verifier Agent
        const verifierSummary =
          reportData?.verification?.verifier_summary || {};
        const verifierChecks = verifierSummary?.checks || {};
        const refundDecision =
          reportData?.refund_processing?.refund_decision || {};
        const canProcessVerifier = reportData?.summary?.can_process || false;
        const verifierDecision = verifierSummary?.decision || "";

        // Determine verification status and next step
        const verificationStatus =
          verifierDecision === "approve_and_process" || canProcessVerifier
            ? "✅ Decision: Approve and Process Refund"
            : verifierDecision === "resend_to_investigator"
            ? "❓ Decision: Resend to Investigator for Clarification"
            : verifierDecision === "human_intervention"
            ? "👤 Decision: Pass for Human Intervention"
            : "Verification completed";

        const nextStep =
          verifierDecision === "approve_and_process" || canProcessVerifier
            ? "Proceed to Communications Agent"
            : verifierDecision === "resend_to_investigator"
            ? "Return to Investigator Agent"
            : "Manual review required";

        return (
          <Card title="Step 4: Verifier Agent">
            <div className="grid md:grid-cols-2 gap-x-8 gap-y-2">
              <InfoItem
                label="Decision"
                value={
                  verifierSummary?.decision ||
                  (refundDecision?.can_process
                    ? canProcessVerifier
                      ? "approve_and_process"
                      : "Manual Review"
                    : "Manual Review")
                }
              />
              <InfoItem
                label="Reason"
                value={
                  verifierSummary?.decision_reason ||
                  refundDecision?.reason ||
                  "All verification checks passed"
                }
              />
              <InfoItem
                label="Can Process"
                value={canProcessVerifier ? "Yes" : "No"}
              />
              <InfoItem
                label="Final Action"
                value={
                  refundDecision?.reason ||
                  refundDecision?.final_action ||
                  reportData?.summary?.final_decision ||
                  "Refund approved"
                }
              />
              <InfoItem
                label="Verification Status"
                value={verificationStatus}
              />
              <InfoItem label="Next Step" value={nextStep} />
              <InfoItem
                label="Reconciliation OK"
                value={verifierSummary?.reconciliation_ok}
              />
              <InfoItem
                label="Sequence OK"
                value={verifierChecks?.sequence_ok}
              />
              <InfoItem
                label="Cross Checks OK"
                value={verifierChecks?.cross_checks_ok}
              />
              <InfoItem
                label="CSV Validation OK"
                value={verifierChecks?.csv_validation_ok}
              />
              <InfoItem
                label="Non Branch OK"
                value={verifierChecks?.non_branch_ok}
              />
              <InfoItem
                label="Sanctions OK"
                value={verifierChecks?.sanctions_ok}
              />
              <InfoItem
                label="FX Loss Within Limit"
                value={verifierChecks?.fx_loss_within_limit}
              />
              <InfoItem
                label="Nostro Match Found"
                value={verifierChecks?.nostro_match_found}
              />
              <InfoItem
                label="Nostro Match Type"
                value={verifierChecks?.nostro_match_type || "none"}
              />
            </div>
          </Card>
        );
      }
      case 5: {
        // Communications Agent
        const commTemplates =
          reportData?.communications?.communication_templates || {};
        const templatesArray = Array.isArray(commTemplates)
          ? commTemplates
          : Object.values(commTemplates);
        const p004Comm = reportData?.parsed_data?.pacs004 || {};
        const p008Comm = reportData?.parsed_data?.pacs008 || {};
        const canProcessComm = reportData?.summary?.can_process || false;
        const commStatus =
          templatesArray.length > 0
            ? "Templates Generated"
            : "Pending Generation";
        const commSummaryStatus = reportData?.communications?.email_payload
          ? "Customer notification prepared and ready for sending"
          : "Communication templates generated";
        const commNextStep = canProcessComm
          ? "Proceed to Investigation Report"
          : "Case requires manual review";

        return (
          <Card title="Step 5: Communications Agent">
            <div className="grid md:grid-cols-2 gap-x-8 gap-y-2">
              <InfoItem
                label="Customer Name"
                value={
                  p008Comm?.dbtr_name || p008Comm?.customer_name || "Unknown"
                }
              />
              <InfoItem
                label="Customer IBAN"
                value={
                  p008Comm?.dbtr_iban || p008Comm?.customer_iban || "Unknown"
                }
              />
              <InfoItem
                label="Case Reference"
                value={
                  reportData?.transaction_id ||
                  reportData?.case_id ||
                  reportData?.prep_logger?.case_id ||
                  "Unknown"
                }
              />
              <InfoItem
                label="Amount"
                value={
                  p004Comm?.rtr_amount || p004Comm?.amount
                    ? `${p004Comm?.rtr_amount || p004Comm?.amount} ${
                        p004Comm?.rtr_ccy || p004Comm?.currency || ""
                      }`
                    : "Unknown"
                }
              />
              <InfoItem label="Communication Status" value={commStatus} />
              <InfoItem
                label="Communication Summary"
                value={commSummaryStatus}
              />
              <InfoItem label="Next Step" value={commNextStep} />
              <InfoItem
                label="Templates Generated"
                value={templatesArray.length}
              />
            </div>
            {templatesArray.length > 0 && (
              <div className="mt-6">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3">
                  Communication Templates:
                </div>
                <div className="space-y-4">
                  {templatesArray.map((template: any, idx: number) => (
                    <div
                      key={idx}
                      className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-4"
                    >
                      <div className="font-semibold mb-2 text-gray-900 dark:text-white">
                        {template.type || `Template ${idx + 1}`}
                      </div>
                      {template.subject && (
                        <div className="text-sm mb-1 text-gray-700 dark:text-gray-300">
                          <strong>Subject:</strong> {template.subject}
                        </div>
                      )}
                      {template.priority && (
                        <div className="text-sm mb-1 text-gray-700 dark:text-gray-300">
                          <strong>Priority:</strong> {template.priority}
                        </div>
                      )}
                      {template.body && (
                        <div className="text-sm mt-2">
                          <strong className="text-gray-700 dark:text-gray-300">
                            Body:
                          </strong>
                          <pre className="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-auto max-h-48 text-gray-900 dark:text-white whitespace-pre-wrap">
                            {template.body}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        );
      }
      case 6: // Investigation Report
        return <ReportTabs reportData={reportData} />;
      case 7: {
        // Case Final Status
        const manualReview = reportData?.manual_review_case || {};
        const canProcessFinal = reportData?.summary?.can_process || false;

        // Determine Final Status - prioritize manual_review_case.status, then processing_status, then derive from can_process
        // If status is "unknown", use approve/process refund information
        let finalStatus =
          manualReview?.status ||
          reportData?.processing_status ||
          reportData?.summary?.final_status ||
          (canProcessFinal ? "Processed" : "Pending");

        // If final status is "unknown", derive from can_process
        if (
          finalStatus?.toLowerCase() === "unknown" ||
          !finalStatus ||
          finalStatus === "N/A"
        ) {
          finalStatus = canProcessFinal
            ? "Approved - Process Refund"
            : "Pending Manual Review";
        }

        // Refund Status: "Approved" if can_process, else "Pending Manual Review"
        const refundStatus = canProcessFinal
          ? "Approved"
          : "Pending Manual Review";

        // Case Status: "Closed - Refund Processed" if can_process, else "Open - Manual Review Required"
        const caseStatus = canProcessFinal
          ? "Closed - Refund Processed"
          : "Open - Manual Review Required";

        // Final Decision/Reason
        const finalDecision =
          reportData?.refund_processing?.refund_decision?.reason ||
          reportData?.refund_flow?.final_decision ||
          reportData?.summary?.reason ||
          (canProcessFinal ? "Refund approved" : "Manual review required");

        // Decision Reason from verification
        const decisionReason =
          reportData?.verification?.verifier_summary?.decision_reason ||
          reportData?.summary?.reason ||
          (canProcessFinal
            ? "All verification checks passed"
            : "All verification checks completed");

        return (
          <Card title="Step 7: Case Final Status">
            <div className="text-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <h4
                className={`text-2xl font-bold ${
                  canProcessFinal ? "text-green-500" : "text-yellow-500"
                }`}
              >
                {canProcessFinal
                  ? "✅ APPROVE AND PROCESS REFUND"
                  : "⏳ PENDING MANUAL REVIEW"}
              </h4>
            </div>
            <div className="mt-6 grid md:grid-cols-2 gap-x-8">
              <InfoItem
                label="Refund Status"
                value={refundStatus}
                isBadge
                badgeType={canProcessFinal ? "success" : "warning"}
              />
              <InfoItem
                label="Case Status"
                value={caseStatus}
                isBadge
                badgeType={canProcessFinal ? "success" : "warning"}
              />
              <InfoItem
                label="Can Process"
                value={canProcessFinal ? "Yes" : "No"}
                isBadge
                badgeType={canProcessFinal ? "success" : "warning"}
              />
              <InfoItem label="Final Status" value={finalStatus} />
              <InfoItem label="Final Decision" value={finalDecision} />
              <InfoItem label="Reason" value={decisionReason} />
              <InfoItem
                label="Description of Reason"
                value={
                  reportData?.refund_processing?.refund_decision?.reason ||
                  reportData?.summary?.reason ||
                  (canProcessFinal
                    ? "Case processing completed successfully"
                    : "Case requires manual review")
                }
              />
              {manualReview?.case_type && (
                <InfoItem label="Case Type" value={manualReview.case_type} />
              )}
              {manualReview?.pending_until && (
                <InfoItem
                  label="Pending Until"
                  value={manualReview.pending_until}
                />
              )}
              <InfoItem
                label="Processing Status"
                value={(() => {
                  const procStatus =
                    reportData?.processing_status ||
                    reportData?.summary?.final_status ||
                    (canProcessFinal ? "Processed" : "Pending");

                  // If status is "unknown", derive from can_process
                  if (
                    procStatus?.toLowerCase() === "unknown" ||
                    !procStatus ||
                    procStatus === "N/A"
                  ) {
                    return canProcessFinal
                      ? "Approved - Process Refund"
                      : "Pending Manual Review";
                  }
                  return procStatus;
                })()}
              />
              {(manualReview?.review_reason ||
                reportData?.flow_checklist?.review_reason) && (
                <InfoItem
                  label="Review Reason"
                  value={
                    manualReview?.review_reason ||
                    reportData?.flow_checklist?.review_reason
                  }
                />
              )}
              {manualReview?.pending_until && (
                <InfoItem
                  label="Pending Until"
                  value={new Date(
                    manualReview.pending_until
                  ).toLocaleDateString()}
                />
              )}
              {manualReview?.priority && (
                <InfoItem label="Priority" value={manualReview.priority} />
              )}
              {reportData?.summary?.credit_account_iban && (
                <InfoItem
                  label="Credit Account IBAN"
                  value={reportData.summary.credit_account_iban}
                />
              )}
            </div>
          </Card>
        );
      }
      default:
        return (
          <Card title="Unknown Step">
            <p className="text-gray-500 dark:text-gray-400">
              Step {step} is not recognized.
            </p>
          </Card>
        );
    }
  } catch (error) {
    console.error("Error rendering step content:", error);
    return (
      <Card title="Error Rendering Content">
        <div className="text-red-500 dark:text-red-400">
          <p className="font-semibold mb-2">
            An error occurred while rendering this step:
          </p>
          <p className="text-sm">
            {error instanceof Error ? error.message : String(error)}
          </p>
        </div>
      </Card>
    );
  }
};

const ReportTabs: React.FC<{ reportData: ReportData }> = ({ reportData }) => {
  const [activeTab, setActiveTab] = useState("details");

  if (!reportData) {
    return (
      <Card title="Report Tabs">
        <p className="text-gray-500 dark:text-gray-400">
          No report data available.
        </p>
      </Card>
    );
  }

  const tabs = [
    { id: "details", label: "Investigation Details" },
    { id: "overview", label: "Process Overview" },
    { id: "graph", label: "Agent Graph" },
    { id: "comms", label: "Communication" },
    { id: "ops", label: "Account Operations" },
  ];

  const renderTabContent = () => {
    try {
      switch (activeTab) {
        case "details":
          return <InvestigationDetailsTab reportData={reportData} />;
        case "overview":
          return <ProcessOverviewTab reportData={reportData} />;
        case "graph":
          return <AgentGraphTab reportData={reportData} />;
        case "comms":
          return <CommunicationTab reportData={reportData} />;
        case "ops":
          return <AccountOperationsTab reportData={reportData} />;
        default:
          return (
            <Card title="Unknown Tab">
              <p className="text-gray-500 dark:text-gray-400">
                Tab {activeTab} is not recognized.
              </p>
            </Card>
          );
      }
    } catch (error) {
      console.error("Error rendering tab content:", error);
      return (
        <Card title="Error Rendering Tab">
          <div className="text-red-500 dark:text-red-400">
            <p className="font-semibold mb-2">
              An error occurred while rendering this tab:
            </p>
            <p className="text-sm">
              {error instanceof Error ? error.message : String(error)}
            </p>
          </div>
        </Card>
      );
    }
  };

  return (
    <div>
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? "border-yellow-500 text-yellow-600 dark:text-yellow-400"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      <div className="mt-6">{renderTabContent()}</div>
    </div>
  );
};

const InvestigationDetailsTab: React.FC<{ reportData: ReportData }> = ({
  reportData,
}) => {
  if (!reportData) {
    return (
      <Card title="Transaction Summary">
        <p className="text-gray-500 dark:text-gray-400">
          No report data available.
        </p>
      </Card>
    );
  }

  const eligibility = reportData?.investigation?.eligibility || {};
  const fxCalc = reportData?.fx_calculation || {};
  const p004 = reportData?.parsed_data?.pacs004 || {};
  const p008 = reportData?.parsed_data?.pacs008 || {};
  const verifierSummary = reportData?.verification?.verifier_summary || {};
  const verifierChecks = verifierSummary?.checks || {};

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card title="Transaction Summary">
          <div className="grid md:grid-cols-2 gap-x-8">
            <InfoItem label="UETR" value={reportData?.uetr || p004?.uetr} />
            <InfoItem
              label="End-to-End ID"
              value={reportData?.transaction_id || p004?.e2e}
            />
            <InfoItem
              label="Customer IBAN"
              value={p004?.cdtr_iban || p008?.dbtr_iban}
            />
            <InfoItem
              label="Return Amount"
              value={
                fxCalc?.returned_amount != null
                  ? `${fxCalc.returned_amount} ${
                      fxCalc.returned_currency ||
                      eligibility?.returned_currency ||
                      "USD"
                    }`
                  : eligibility?.returned_amount != null
                  ? `${eligibility.returned_amount} ${
                      eligibility.returned_currency || "USD"
                    }`
                  : "N/A"
              }
            />
            <InfoItem
              label="FX Loss (AUD)"
              value={
                fxCalc?.loss_aud != null
                  ? `AUD ${fxCalc.loss_aud.toFixed(2)}`
                  : eligibility?.fx_loss_aud != null
                  ? `AUD ${eligibility.fx_loss_aud.toFixed(2)}`
                  : "N/A"
              }
            />
            <InfoItem
              label="Refund Decision"
              value={
                reportData?.summary?.can_process === true
                  ? "Can Process"
                  : reportData?.summary?.can_process === false
                  ? "Can't Process"
                  : reportData?.refund_flow?.final_decision || "N/A"
              }
            />
            <InfoItem
              label="Final Status"
              value={(() => {
                const canProcess = reportData?.summary?.can_process || false;
                const status =
                  reportData?.processing_status ||
                  reportData?.summary?.final_status ||
                  (canProcess ? "Processed" : "Pending");

                // If status is "unknown", derive from can_process
                if (
                  status?.toLowerCase() === "unknown" ||
                  !status ||
                  status === "N/A"
                ) {
                  return canProcess
                    ? "Approved - Process Refund"
                    : "Pending Manual Review";
                }
                return status;
              })()}
            />
          </div>
        </Card>
        <Card title="FX Details">
          <div className="grid md:grid-cols-2 gap-x-8">
            <InfoItem
              label="Original Amount"
              value={
                fxCalc?.original_amount != null
                  ? `${fxCalc.original_amount} ${
                      fxCalc.original_currency || ""
                    }`
                  : eligibility?.original_amount != null
                  ? `${eligibility.original_amount} ${
                      eligibility.original_currency || ""
                    }`
                  : "N/A"
              }
            />
            <InfoItem
              label="Returned Amount"
              value={
                fxCalc?.returned_amount != null
                  ? `${fxCalc.returned_amount} ${
                      fxCalc.returned_currency || ""
                    }`
                  : eligibility?.returned_amount != null
                  ? `${eligibility.returned_amount} ${
                      eligibility.returned_currency || ""
                    }`
                  : "N/A"
              }
            />
            <InfoItem
              label="Original Amount (AUD)"
              value={
                fxCalc?.original_amount_aud != null
                  ? `AUD ${fxCalc.original_amount_aud.toFixed(2)}`
                  : eligibility?.original_amount_aud != null
                  ? `AUD ${eligibility.original_amount_aud.toFixed(2)}`
                  : "N/A"
              }
            />
            <InfoItem
              label="Returned Amount (AUD)"
              value={
                fxCalc?.returned_amount_aud != null
                  ? `AUD ${fxCalc.returned_amount_aud.toFixed(2)}`
                  : eligibility?.returned_amount_aud != null
                  ? `AUD ${eligibility.returned_amount_aud.toFixed(2)}`
                  : "N/A"
              }
            />
            <InfoItem
              label="FX Loss (AUD)"
              value={
                fxCalc?.loss_aud != null
                  ? `AUD ${fxCalc.loss_aud.toFixed(2)}`
                  : eligibility?.fx_loss_aud != null
                  ? `AUD ${eligibility.fx_loss_aud.toFixed(2)}`
                  : "N/A"
              }
            />
            <InfoItem
              label="Calculation Method"
              value={fxCalc?.calculation_method || "N/A"}
            />
          </div>
        </Card>
      </div>
      <div className="lg:col-span-1 space-y-6">
        <Card title="Workflow Verdict">
          <InfoItem
            label="Can Process"
            value={reportData?.summary?.can_process || false}
            isBadge
            badgeType={reportData?.summary?.can_process ? "success" : "warning"}
          />
          <InfoItem
            label="Manual Review"
            value={reportData?.flow_checklist?.manual_review_required}
            isBadge
            badgeType={
              reportData?.flow_checklist?.manual_review_required
                ? "warning"
                : "info"
            }
          />
        </Card>
        <Card title="Key Checks">
          <InfoItem
            label="Sanctions"
            value={
              verifierChecks?.sanctions_ok || eligibility?.sanctions_ok
                ? "Passed"
                : "Failed"
            }
            isBadge
            badgeType={
              verifierChecks?.sanctions_ok || eligibility?.sanctions_ok
                ? "success"
                : "danger"
            }
          />
          <InfoItem
            label="CSV Validation"
            value={
              verifierChecks?.csv_validation_ok ||
              reportData?.investigation?.csv_validation?.ok
                ? "Passed"
                : "Failed"
            }
            isBadge
            badgeType={
              verifierChecks?.csv_validation_ok ||
              reportData?.investigation?.csv_validation?.ok
                ? "success"
                : "danger"
            }
          />
          <InfoItem
            label="FX Loss ≤ 300"
            value={
              verifierChecks?.fx_loss_within_limit ||
              eligibility?.fx_loss_within_limit
            }
            isBadge
            badgeType={
              verifierChecks?.fx_loss_within_limit ||
              eligibility?.fx_loss_within_limit
                ? "success"
                : "warning"
            }
          />
        </Card>
      </div>
    </div>
  );
};

const AccountOperationsTab: React.FC<{ reportData: ReportData }> = ({
  reportData,
}) => {
  // Account operations can be at root level or in refund_processing
  const operations =
    reportData?.account_operations ||
    reportData?.refund_processing?.refund_decision?.account_operations ||
    reportData?.refund_processing?.account_operations ||
    reportData?.refund_decision?.account_operations ||
    [];

  // Helper function to parse balance string (e.g., "USD -34,930.00" -> -34930.00)
  const parseBalance = (
    balanceStr: string | number | null | undefined,
    currency: string = ""
  ): number => {
    if (balanceStr == null) return 0;
    if (typeof balanceStr === "number") return balanceStr;

    // Remove currency, commas, and whitespace
    let cleaned = balanceStr.toString();
    if (currency) cleaned = cleaned.replace(currency, "");
    cleaned = cleaned.replace(/,/g, "").trim();

    try {
      return parseFloat(cleaned) || 0;
    } catch {
      return 0;
    }
  };

  // Helper function to get account type badge
  const getAccountType = (
    accountName: string = ""
  ): { label: string; className: string } => {
    const name = accountName.toLowerCase();
    if (name.includes("nostro")) {
      return {
        label: "Nostro",
        className:
          "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
      };
    } else if (name.includes("fca")) {
      return {
        label: "FCA",
        className:
          "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
      };
    } else if (name.includes("customer")) {
      return {
        label: "Customer",
        className:
          "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
      };
    }
    return {
      label: "Other",
      className:
        "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
    };
  };

  return (
    <div className="space-y-6">
      {operations.length > 0 ? (
        <>
          {/* Balance Changes Summary Table */}
          <Card title="Balance Changes Summary">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Account
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Currency
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Balance Before
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Operation
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Balance After
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Net Change
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {operations.map((op: any, i: number) => {
                    const opType = (op.operation_type || "").toUpperCase();
                    const isCredit = opType === "CREDIT" || opType === "C";
                    const currency = op.currency || "";
                    const accountType = getAccountType(op.account_name);

                    // Parse balances (they come as formatted strings like "USD -34,930.00")
                    const balanceBefore = parseBalance(
                      op.balance_before,
                      currency
                    );
                    const balanceAfter = parseBalance(
                      op.balance_after,
                      currency
                    );
                    const netChange = balanceAfter - balanceBefore;

                    // Format amount
                    const amount =
                      typeof op.amount === "number"
                        ? op.amount
                        : parseFloat(op.amount || 0);

                    return (
                      <tr key={i}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="font-medium text-gray-900 dark:text-white">
                            {op.account_name || "N/A"}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {op.account_number || op.account_iban || ""}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span
                            className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${accountType.className}`}
                          >
                            {accountType.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {currency || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono text-gray-900 dark:text-white">
                          {op.balance_before != null
                            ? String(op.balance_before)
                            : "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                          <span
                            className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              isCredit
                                ? "bg-green-500 text-white"
                                : "bg-red-500 text-white"
                            }`}
                          >
                            {opType || "N/A"}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold text-gray-900 dark:text-white">
                          {op.amount != null && !isNaN(amount)
                            ? `${amount.toFixed(1)} ${currency}`
                            : "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono text-gray-900 dark:text-white">
                          {op.balance_after != null
                            ? String(op.balance_after)
                            : "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold">
                          <span
                            className={
                              netChange >= 0
                                ? "text-green-600 dark:text-green-400"
                                : "text-red-600 dark:text-red-400"
                            }
                          >
                            {currency} {netChange.toFixed(2)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Detailed Operations Cards */}
          <Card title="Detailed Operations">
            <div className="grid md:grid-cols-2 gap-4">
              {operations.map((op: any, i: number) => {
                const opType = (op.operation_type || "").toUpperCase();
                const isCredit = opType === "CREDIT" || opType === "C";
                const currency = op.currency || "";
                const amount =
                  typeof op.amount === "number"
                    ? op.amount
                    : parseFloat(op.amount || 0);

                return (
                  <div
                    key={i}
                    className={`p-4 rounded-lg border-2 ${
                      isCredit
                        ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                        : "border-red-500 bg-red-50 dark:bg-red-900/20"
                    }`}
                  >
                    <div className="flex justify-between items-center mb-3">
                      <span
                        className={`px-3 py-1 rounded font-semibold text-sm ${
                          isCredit
                            ? "bg-green-500 text-white"
                            : "bg-red-500 text-white"
                        }`}
                      >
                        {opType}
                      </span>
                      <span className="font-mono font-semibold text-gray-900 dark:text-white">
                        {amount.toFixed(1)} {currency}
                      </span>
                    </div>
                    <div className="mb-3">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {op.account_name || "N/A"}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {op.account_number || op.account_iban || ""}
                      </div>
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">
                          Before:
                        </span>
                        <span className="font-mono text-gray-900 dark:text-white">
                          {op.balance_before != null
                            ? String(op.balance_before)
                            : "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">
                          After:
                        </span>
                        <span className="font-mono text-gray-900 dark:text-white">
                          {op.balance_after != null
                            ? String(op.balance_after)
                            : "N/A"}
                        </span>
                      </div>
                    </div>
                    {op.reference && (
                      <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Reference: {op.reference}
                        </div>
                        {op.description && (
                          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            {op.description}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>
        </>
      ) : (
        <Card title="Account Operations">
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No account operations recorded.
          </div>
        </Card>
      )}
    </div>
  );
};

const ProcessOverviewTab: React.FC<{ reportData: ReportData }> = ({
  reportData,
}) => {
  const checklist = reportData?.flow_checklist?.checks || {};
  const refundDecision =
    reportData?.refund_processing?.refund_decision ||
    reportData?.refund_decision ||
    {};
  const d1D9Decisions =
    reportData?.summary?.d1_d9_decisions ||
    refundDecision?.d1_d9_decisions ||
    {};
  const eligibility = reportData?.investigation?.eligibility || {};
  const verifierSummary = reportData?.verification?.verifier_summary || {};
  const verifierChecks = verifierSummary?.checks || {};
  const fxCalc = reportData?.fx_calculation || {};
  const prepLogger = reportData?.prep_logger?.email_payload || {};
  const nostroResult =
    verifierSummary?.nostro_result ||
    reportData?.verification?.nostro_result ||
    {};
  const commTemplates =
    reportData?.communications?.communication_templates || {};
  const p004 = reportData?.parsed_data?.pacs004 || {};
  const p008 = reportData?.parsed_data?.pacs008 || {};

  // Helper for chip/badge colors
  const getChipClass = (
    value: boolean | string | null | undefined,
    type: "pass" | "fail" | "info" = "info"
  ) => {
    if (type === "pass") {
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
    } else if (type === "fail") {
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
    }
    return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
  };

  const getDecisionChip = (decision: string) => {
    if (decision === "Yes") return getChipClass(true, "pass");
    if (decision === "No") return getChipClass(false, "fail");
    return getChipClass(null, "info");
  };

  return (
    <div className="space-y-6">
      <Card title="Comprehensive Process Overview">
        {/* Visual Decision Flow */}
        <div className="mb-8">
          <h4 className="text-lg font-semibold mb-4">
            📊 Visual Decision Flow
          </h4>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <h5 className="font-semibold mb-3">
              Pre-Flow Checklist (flow_.md)
            </h5>
            <div className="flex flex-wrap items-center gap-3">
              <div className="bg-green-500 text-white px-4 py-2 rounded font-semibold">
                Start
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-3 py-1 rounded text-sm text-white ${
                  checklist?.payments_team_rejection_email
                    ? "bg-red-500"
                    : "bg-green-500"
                }`}
              >
                Email Rejection
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-3 py-1 rounded text-sm text-white ${
                  checklist?.correct_payment_attached
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              >
                Correct Payment
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-3 py-1 rounded text-sm text-white ${
                  checklist?.has_mt103_and_202 ? "bg-red-500" : "bg-green-500"
                }`}
              >
                MT103/202
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-3 py-1 rounded text-sm text-white ${
                  checklist?.is_aud_payment ? "bg-red-500" : "bg-green-500"
                }`}
              >
                {checklist?.is_aud_payment ? "AUD Payment" : "Not AUD Payment"}
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-3 py-1 rounded text-sm text-white ${
                  fxCalc?.exceeds_limit ? "bg-red-500" : "bg-green-500"
                }`}
              >
                FX ≤ $300
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-xl">
                →
              </span>
              <div
                className={`px-4 py-2 rounded font-semibold text-white ${
                  reportData?.flow_checklist?.manual_review_required
                    ? "bg-red-500"
                    : "bg-yellow-500 text-black"
                }`}
              >
                {reportData?.flow_checklist?.manual_review_required
                  ? "Manual Review"
                  : "Proceed to Refund"}
              </div>
            </div>
          </div>
        </div>

        {/* Refund Decision Tree (D1-D9) */}
        <div className="mb-8">
          <h4 className="text-lg font-semibold mb-4">
            Refund Decision Tree (D1-D9)
          </h4>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="space-y-4">
              {["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"].map(
                (d) => {
                  const decision = d1D9Decisions[d] || {};
                  const decisionValue = decision.decision || "N/A";
                  const statement = decision.statement || "Not processed";
                  const labels: Record<string, string> = {
                    D1: "D1: FCY?",
                    D2: "D2: Nostro?",
                    D3: "D3: FCA?",
                    D4: "D4: MT103/202?",
                    D5: "D5: Amendment?",
                    D6: "D6: No Charges?",
                    D7: "D7: Branch?",
                    D8: "D8: Markets?",
                    D9: "D9: Email?",
                  };
                  return (
                    <div key={d} className="flex items-center gap-4">
                      <div className="bg-yellow-500 text-black px-3 py-1 rounded text-sm font-semibold">
                        {labels[d]}
                      </div>
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${getDecisionChip(
                          decisionValue
                        )}`}
                      >
                        {decisionValue}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs ${getChipClass(
                          null,
                          "info"
                        )}`}
                      >
                        {statement}
                      </span>
                    </div>
                  );
                }
              )}
              <div className="flex items-center gap-4 pt-2">
                <div
                  className={`px-4 py-2 rounded font-semibold text-white ${
                    refundDecision?.can_process ||
                    reportData?.summary?.can_process
                      ? "bg-green-500"
                      : "bg-red-500"
                  }`}
                >
                  {refundDecision?.can_process ||
                  reportData?.summary?.can_process
                    ? "Refund Processed"
                    : "Refund Failed"}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Agent Results */}
        <div>
          <h4 className="text-lg font-semibold mb-4">
            🔍 Detailed Agent Results
          </h4>

          {/* Logger Agent */}
          <details className="mb-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <summary className="p-4 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
              📝 Logger Agent —{" "}
              <span
                className={
                  getChipClass(!!prepLogger?.body, "info") +
                  " px-2 py-1 rounded text-xs ml-2"
                }
              >
                {prepLogger?.body ? "Prepared" : "No Email"}
              </span>
            </summary>
            <div className="p-4 space-y-3">
              <div className="grid md:grid-cols-2 gap-4">
                <InfoItem
                  label="Subject"
                  value={prepLogger?.subject || "return of funds"}
                />
                <InfoItem
                  label="Reference"
                  value={prepLogger?.reference || "N/A"}
                />
                <InfoItem
                  label="Recipient"
                  value={
                    prepLogger?.customer_email
                      ? `${prepLogger?.customer_name || ""} <${
                          prepLogger.customer_email
                        }>`
                      : "N/A"
                  }
                />
              </div>
              {prepLogger?.body && (
                <div>
                  <div className="font-semibold mb-2">Email Body</div>
                  <pre className="whitespace-pre-wrap bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-3 text-xs overflow-auto max-h-64">
                    {prepLogger.body}
                  </pre>
                </div>
              )}
            </div>
          </details>

          {/* Investigation Agent */}
          <details className="mb-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <summary className="p-4 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
              🔍 Investigation Agent —{" "}
              <span
                className={`px-2 py-1 rounded text-xs ml-2 ${
                  verifierChecks?.csv_validation_ok &&
                  verifierChecks?.cross_checks_ok
                    ? getChipClass(true, "pass")
                    : getChipClass(false, "fail")
                }`}
              >
                {verifierChecks?.csv_validation_ok &&
                verifierChecks?.cross_checks_ok
                  ? "PASS"
                  : "FAIL"}
              </span>
            </summary>
            <div className="p-4">
              <div className="grid md:grid-cols-2 gap-4">
                <InfoItem label="UETR" value={p004?.uetr || reportData?.uetr} />
                <InfoItem
                  label="E2E ID"
                  value={p004?.e2e || reportData?.transaction_id}
                />
                <InfoItem
                  label="IBAN"
                  value={p004?.cdtr_iban || p008?.dbtr_iban}
                />
                <InfoItem
                  label="Return Reason"
                  value={eligibility?.reason || "N/A"}
                />
                <InfoItem
                  label="Reason Info"
                  value={eligibility?.reason_info || "N/A"}
                />
                <InfoItem
                  label="Auto Refund Eligible"
                  value={eligibility?.eligible_auto_refund ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    eligibility?.eligible_auto_refund ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Customer Valid"
                  value={
                    reportData?.investigation?.csv_validation?.ok ? "Yes" : "No"
                  }
                  isBadge
                  badgeType={
                    reportData?.investigation?.csv_validation?.ok
                      ? "success"
                      : "danger"
                  }
                />
                <InfoItem
                  label="Cross Checks"
                  value={
                    reportData?.investigation?.cross_errors?.length === 0
                      ? "OK"
                      : "FAIL"
                  }
                  isBadge
                  badgeType={
                    reportData?.investigation?.cross_errors?.length === 0
                      ? "success"
                      : "danger"
                  }
                />
                <InfoItem
                  label="Currency Mismatch"
                  value={eligibility?.currency_mismatch ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    eligibility?.currency_mismatch ? "danger" : "success"
                  }
                />
              </div>
            </div>
          </details>

          {/* Actioning Agent */}
          <details className="mb-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <summary className="p-4 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
              ⚙️ Actioning Agent —{" "}
              <span
                className={
                  getChipClass(
                    !fxCalc?.exceeds_limit &&
                      !reportData?.flow_checklist?.manual_review_required &&
                      nostroResult?.found,
                    "pass"
                  ) + " px-2 py-1 rounded text-xs ml-2"
                }
              >
                Overview
              </span>
            </summary>
            <div className="p-4 space-y-4">
              {/* FX Calculation */}
              <details className="border border-gray-200 dark:border-gray-600 rounded-lg">
                <summary className="p-3 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700">
                  💱 FX Calculation
                </summary>
                <div className="p-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <InfoItem
                      label="Original Amount"
                      value={`${fxCalc?.original_amount || 0} ${
                        fxCalc?.original_currency || ""
                      }`}
                    />
                    <InfoItem
                      label="Returned Amount"
                      value={`${fxCalc?.returned_amount || 0} ${
                        fxCalc?.returned_currency || ""
                      }`}
                    />
                    <InfoItem
                      label="Original AUD"
                      value={`$${fxCalc?.original_amount_aud || 0}`}
                    />
                    <InfoItem
                      label="Returned AUD"
                      value={`$${fxCalc?.returned_amount_aud || 0}`}
                    />
                    <InfoItem
                      label="FX Loss AUD"
                      value={`$${fxCalc?.loss_aud || 0}`}
                      isBadge
                      badgeType={fxCalc?.exceeds_limit ? "danger" : "success"}
                    />
                    <InfoItem
                      label="Exceeds $300"
                      value={fxCalc?.exceeds_limit ? "Yes" : "No"}
                      isBadge
                      badgeType={fxCalc?.exceeds_limit ? "danger" : "success"}
                    />
                    <InfoItem
                      label="FCA Account Found"
                      value={fxCalc?.fca_account_found ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        fxCalc?.fca_account_found ? "success" : "danger"
                      }
                    />
                    <InfoItem
                      label="Calculation Method"
                      value={fxCalc?.calculation_method || "N/A"}
                    />
                  </div>
                </div>
              </details>

              {/* Checklist */}
              <details className="border border-gray-200 dark:border-gray-600 rounded-lg">
                <summary className="p-3 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700">
                  ✅ Checklist
                </summary>
                <div className="p-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <InfoItem
                      label="Email Rejection"
                      value={
                        checklist?.payments_team_rejection_email ? "Yes" : "No"
                      }
                      isBadge
                      badgeType={
                        checklist?.payments_team_rejection_email
                          ? "danger"
                          : "success"
                      }
                    />
                    <InfoItem
                      label="Correct Payment"
                      value={checklist?.correct_payment_attached ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.correct_payment_attached
                          ? "success"
                          : "danger"
                      }
                    />
                    <InfoItem
                      label="Has MT103/202"
                      value={checklist?.has_mt103_and_202 ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.has_mt103_and_202 ? "danger" : "success"
                      }
                    />
                    <InfoItem
                      label="AUD Payment"
                      value={checklist?.is_aud_payment ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.is_aud_payment ? "danger" : "success"
                      }
                    />
                    <InfoItem
                      label="Amendment Sent"
                      value={
                        checklist?.amendment_previously_sent ? "Yes" : "No"
                      }
                      isBadge
                      badgeType={
                        checklist?.amendment_previously_sent
                          ? "danger"
                          : "success"
                      }
                    />
                    <InfoItem
                      label="CBA FCA Return"
                      value={checklist?.returned_due_to_cba_fca ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.returned_due_to_cba_fca
                          ? "danger"
                          : "success"
                      }
                    />
                    <InfoItem
                      label="No Funds Due Charges"
                      value={checklist?.no_funds_due_to_charges ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.no_funds_due_to_charges
                          ? "danger"
                          : "success"
                      }
                    />
                    <InfoItem
                      label="Return Reason Clear"
                      value={checklist?.return_reason_clear ? "Yes" : "No"}
                      isBadge
                      badgeType={
                        checklist?.return_reason_clear ? "success" : "danger"
                      }
                    />
                    <InfoItem
                      label="Manual Review Required"
                      value={
                        reportData?.flow_checklist?.manual_review_required
                          ? "Yes"
                          : "No"
                      }
                      isBadge
                      badgeType={
                        reportData?.flow_checklist?.manual_review_required
                          ? "danger"
                          : "success"
                      }
                    />
                  </div>
                </div>
              </details>

              {/* Nostro */}
              <details className="border border-gray-200 dark:border-gray-600 rounded-lg">
                <summary className="p-3 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700">
                  🏦 Nostro
                </summary>
                <div className="p-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <InfoItem
                      label="Match Found"
                      value={nostroResult?.found ? "Yes" : "No"}
                      isBadge
                      badgeType={nostroResult?.found ? "success" : "danger"}
                    />
                    <InfoItem
                      label="Match Type"
                      value={nostroResult?.match_type || "none"}
                    />
                    <InfoItem
                      label="Nostro Entry"
                      value={
                        nostroResult?.nostro_entry
                          ? String(nostroResult.nostro_entry)
                          : "N/A"
                      }
                    />
                  </div>
                </div>
              </details>

              {/* Refund */}
              <details className="border border-gray-200 dark:border-gray-600 rounded-lg">
                <summary className="p-3 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700">
                  💰 Refund (D1–D9)
                </summary>
                <div className="p-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <InfoItem
                      label="Can Process"
                      value={
                        refundDecision?.can_process ||
                        reportData?.summary?.can_process
                          ? "Yes"
                          : "No"
                      }
                      isBadge
                      badgeType={
                        refundDecision?.can_process ||
                        reportData?.summary?.can_process
                          ? "success"
                          : "danger"
                      }
                    />
                    <InfoItem
                      label="Final Action"
                      value={
                        refundDecision?.reason ||
                        reportData?.summary?.reason ||
                        "N/A"
                      }
                    />
                    <InfoItem
                      label="Account Operations"
                      value={(
                        reportData?.refund_processing?.refund_decision
                          ?.account_operations?.length ||
                        reportData?.refund_decision?.account_operations
                          ?.length ||
                        reportData?.account_operations?.length ||
                        0
                      ).toString()}
                    />
                    <InfoItem
                      label="Credit Account IBAN"
                      value={
                        refundDecision?.credit_account_iban ||
                        reportData?.summary?.credit_account_iban ||
                        p008?.dbtr_iban ||
                        "N/A"
                      }
                    />
                  </div>
                </div>
              </details>
            </div>
          </details>

          {/* Verifier Agent */}
          <details className="mb-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <summary className="p-4 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
              ✅ Verifier Agent —{" "}
              <span
                className={`px-2 py-1 rounded text-xs ml-2 ${
                  verifierSummary?.reconciliation_ok
                    ? getChipClass(true, "pass")
                    : getChipClass(false, "fail")
                }`}
              >
                {verifierSummary?.reconciliation_ok ? "PASS" : "FAIL"}
              </span>
            </summary>
            <div className="p-4">
              <div className="grid md:grid-cols-2 gap-4">
                <InfoItem
                  label="Reconciliation OK"
                  value={verifierSummary?.reconciliation_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierSummary?.reconciliation_ok ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Sequence OK"
                  value={verifierChecks?.sequence_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={verifierChecks?.sequence_ok ? "success" : "danger"}
                />
                <InfoItem
                  label="Cross Checks OK"
                  value={verifierChecks?.cross_checks_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.cross_checks_ok ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="CSV Validation OK"
                  value={verifierChecks?.csv_validation_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.csv_validation_ok ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Non Branch OK"
                  value={verifierChecks?.non_branch_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.non_branch_ok ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Sanctions OK"
                  value={verifierChecks?.sanctions_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.sanctions_ok ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="FX Loss Within Limit"
                  value={verifierChecks?.fx_loss_within_limit ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.fx_loss_within_limit ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Nostro Match Found"
                  value={verifierChecks?.nostro_match_found ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.nostro_match_found ? "success" : "danger"
                  }
                />
                <InfoItem
                  label="Process Flow OK"
                  value={verifierChecks?.process_flow_ok ? "Yes" : "No"}
                  isBadge
                  badgeType={
                    verifierChecks?.process_flow_ok ? "success" : "danger"
                  }
                />
              </div>
            </div>
          </details>

          {/* Communications Agent */}
          <details className="mb-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <summary className="p-4 font-semibold cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
              📧 Communications Agent —{" "}
              <span
                className={
                  getChipClass(true, "pass") + " px-2 py-1 rounded text-xs ml-2"
                }
              >
                PREPARED
              </span>
            </summary>
            <div className="p-4">
              <div className="grid md:grid-cols-2 gap-4">
                <InfoItem
                  label="Templates Generated"
                  value={
                    Array.isArray(commTemplates)
                      ? commTemplates.length
                      : Object.keys(commTemplates || {}).length
                  }
                />
                <InfoItem
                  label="Customer Notification"
                  value={
                    (commTemplates as any)?.customer_notification?.status ||
                    (reportData?.summary?.can_process ? "SENT" : "N/A")
                  }
                />
                <InfoItem
                  label="Branch Advisory"
                  value={
                    (commTemplates as any)?.branch_advisory?.status ||
                    (reportData?.summary?.can_process ? "Prepared" : "N/A")
                  }
                />
                <InfoItem
                  label="Ops Advisory Priority"
                  value={
                    (commTemplates as any)?.ops_advisory?.priority || "Normal"
                  }
                />
                <InfoItem
                  label="Decision Summary"
                  value={
                    reportData?.summary?.reason ||
                    refundDecision?.reason ||
                    "N/A"
                  }
                />
                <InfoItem
                  label="Account Ops Count"
                  value={(
                    reportData?.summary?.account_operations_count ||
                    reportData?.refund_decision?.account_operations?.length ||
                    reportData?.account_operations?.length ||
                    0
                  ).toString()}
                />
              </div>
            </div>
          </details>
        </div>
      </Card>
    </div>
  );
};

const AgentGraphTab: React.FC<{ reportData: ReportData }> = ({
  reportData,
}) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [modalData, setModalData] = useState<{
    title: string;
    rows: Array<[string, string]>;
  } | null>(null);

  // Helper function to extract value with multiple fallbacks
  // Returns the first non-empty value, or "N/A" if all are empty
  const getValue = (
    ...values: (string | number | boolean | undefined | null)[]
  ): string => {
    for (const val of values) {
      // Handle different types: accept 0, false, and empty strings as valid values
      if (val === 0 || val === false) {
        return String(val);
      }
      if (val !== undefined && val !== null && val !== "" && val !== "-") {
        return String(val);
      }
    }
    return "N/A";
  };

  // Extract data for tooltips with comprehensive fallbacks
  const prepLogger = reportData?.prep_logger?.email_payload || {};
  const p004 = reportData?.parsed_data?.pacs004 || {};
  const p008 = reportData?.parsed_data?.pacs008 || {};
  const eligibility =
    reportData?.investigation?.eligibility ||
    reportData?.investigation?.summary ||
    {};
  const csvValidation = reportData?.investigation?.csv_validation || {};
  const verifierSummary = reportData?.verification?.verifier_summary || {};
  const verifierChecks =
    verifierSummary?.checks || reportData?.verification || {};
  const fxCalc = reportData?.fx_calculation || reportData?.fx || {};
  const checklist =
    reportData?.flow_checklist?.checks || reportData?.flow_checklist || {};
  const nostroResult =
    verifierSummary?.nostro_result ||
    reportData?.verification?.nostro_result ||
    verifierChecks?.nostro_result ||
    {};
  const refundDecision =
    reportData?.refund_processing?.refund_decision ||
    reportData?.refund_decision ||
    reportData?.summary ||
    {};
  const commTemplates =
    reportData?.communications?.communication_templates || {};
  const canProcess =
    refundDecision?.can_process || reportData?.summary?.can_process || false;

  // Agent data for tooltips
  const agentData: Record<
    string,
    { title: string; rows: Array<[string, string]> }
  > = {
    prep_logger: {
      title: "Logger Agent",
      rows: [
        [
          "Case ID",
          getValue(
            reportData?.prep_logger?.case_id,
            reportData?.case_id,
            reportData?.transaction_id
          ),
        ],
        [
          "Email Subject",
          getValue(
            prepLogger?.subject,
            reportData?.communications?.email_payload?.subject,
            reportData?.prep_logger?.email_payload?.subject
          ),
        ],
        [
          "Customer Email",
          getValue(
            prepLogger?.customer_email,
            reportData?.prep_logger?.email_payload?.customer_email
          ),
        ],
        [
          "Transaction Ref",
          getValue(
            prepLogger?.reference,
            reportData?.prep_logger?.email_payload?.reference,
            reportData?.transaction_id
          ),
        ],
        [
          "Amount",
          prepLogger?.amount || reportData?.prep_logger?.email_payload?.amount
            ? `${
                prepLogger?.amount ||
                reportData?.prep_logger?.email_payload?.amount
              } ${
                prepLogger?.currency ||
                reportData?.prep_logger?.email_payload?.currency ||
                ""
              }`
            : "N/A",
        ],
        [
          "Currency",
          getValue(
            prepLogger?.currency,
            reportData?.prep_logger?.email_payload?.currency,
            p004?.currency,
            p008?.currency
          ),
        ],
        [
          "Return Reason",
          getValue(
            prepLogger?.return_reason,
            eligibility?.return_reason,
            eligibility?.reason,
            p004?.return_reason
          ),
        ],
        ["Anonymized", reportData?.prep_logger?.anonymized_data ? "Yes" : "No"],
      ],
    },
    investigator: {
      title: "Investigation Agent",
      rows: [
        [
          "UETR",
          getValue(
            p004?.uetr,
            reportData?.uetr,
            reportData?.investigation?.summary?.uetr,
            eligibility?.uetr
          ),
        ],
        [
          "E2E",
          getValue(
            p004?.e2e,
            p004?.e2e_id,
            reportData?.transaction_id,
            reportData?.investigation?.summary?.e2e_id
          ),
        ],
        [
          "IBAN",
          getValue(
            p004?.cdtr_iban,
            p004?.dbtr_iban,
            p008?.cdtr_iban,
            p008?.dbtr_iban,
            eligibility?.customer_account,
            reportData?.investigation?.summary?.customer_account
          ),
        ],
        [
          "Return Reason",
          getValue(
            eligibility?.reason,
            eligibility?.return_reason,
            reportData?.investigation?.summary?.return_reason,
            p004?.return_reason
          ),
        ],
        [
          "Reason Info",
          getValue(
            eligibility?.reason_info,
            reportData?.investigation?.summary?.return_reason_info,
            p004?.return_reason_info
          ),
        ],
        [
          "Auto Refund Eligible",
          eligibility?.eligible_auto_refund !== undefined
            ? eligibility.eligible_auto_refund
              ? "Yes"
              : "No"
            : eligibility?.auto_refund_eligible !== undefined
            ? eligibility.auto_refund_eligible
              ? "Yes"
              : "No"
            : reportData?.investigation?.summary?.auto_refund_eligible !==
              undefined
            ? reportData.investigation.summary.auto_refund_eligible
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Customer Valid",
          csvValidation?.ok !== undefined
            ? csvValidation.ok
              ? "Yes"
              : "No"
            : eligibility?.customer_valid !== undefined
            ? eligibility.customer_valid
              ? "Yes"
              : "No"
            : reportData?.investigation?.summary?.customer_valid !== undefined
            ? reportData.investigation.summary.customer_valid
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Cross Checks",
          reportData?.investigation?.cross_errors?.length === 0
            ? "OK"
            : reportData?.investigation?.cross_errors?.length
            ? "FAIL"
            : eligibility?.cross_checks === "OK"
            ? "OK"
            : eligibility?.cross_checks
            ? "FAIL"
            : "N/A",
        ],
      ],
    },
    actioning: {
      title: "Actioning Agent",
      rows: [
        [
          "FX Loss AUD",
          fxCalc?.loss_aud !== undefined
            ? `$${fxCalc.loss_aud}`
            : fxCalc?.fx_loss_aud !== undefined
            ? `$${fxCalc.fx_loss_aud}`
            : "N/A",
        ],
        [
          "Exceeds $300",
          fxCalc?.exceeds_limit !== undefined
            ? fxCalc.exceeds_limit
              ? "Yes"
              : "No"
            : fxCalc?.exceeds_300 !== undefined
            ? fxCalc.exceeds_300
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "FCA Account Found",
          fxCalc?.fca_account_found !== undefined
            ? fxCalc.fca_account_found
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Nostro Match",
          nostroResult?.found !== undefined
            ? nostroResult.found
              ? "Yes"
              : "No"
            : verifierChecks?.nostro_match_found !== undefined
            ? verifierChecks.nostro_match_found
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Manual Review",
          reportData?.flow_checklist?.manual_review_required !== undefined
            ? reportData.flow_checklist.manual_review_required
              ? "Yes"
              : "No"
            : checklist?.manual_review_required !== undefined
            ? checklist.manual_review_required
              ? "Yes"
              : "No"
            : "N/A",
        ],
      ],
    },
    fx: {
      title: "FX Calculation",
      rows: [
        [
          "Original Amount",
          fxCalc?.original_amount || fxCalc?.original_amount_aud
            ? `${fxCalc?.original_amount || fxCalc?.original_amount_aud} ${
                fxCalc?.original_currency || ""
              }`
            : "N/A",
        ],
        [
          "Returned Amount",
          fxCalc?.returned_amount || fxCalc?.returned_amount_aud
            ? `${fxCalc?.returned_amount || fxCalc?.returned_amount_aud} ${
                fxCalc?.returned_currency || ""
              }`
            : "N/A",
        ],
        [
          "Original AUD",
          fxCalc?.original_amount_aud !== undefined
            ? `$${fxCalc.original_amount_aud}`
            : fxCalc?.original_aud !== undefined
            ? `$${fxCalc.original_aud}`
            : "N/A",
        ],
        [
          "Returned AUD",
          fxCalc?.returned_amount_aud !== undefined
            ? `$${fxCalc.returned_amount_aud}`
            : fxCalc?.returned_aud !== undefined
            ? `$${fxCalc.returned_aud}`
            : "N/A",
        ],
        [
          "FX Loss AUD",
          fxCalc?.loss_aud !== undefined
            ? `$${fxCalc.loss_aud}`
            : fxCalc?.fx_loss_aud !== undefined
            ? `$${fxCalc.fx_loss_aud}`
            : "N/A",
        ],
        [
          "Exceeds $300",
          fxCalc?.exceeds_limit !== undefined
            ? fxCalc.exceeds_limit
              ? "Yes"
              : "No"
            : fxCalc?.exceeds_300 !== undefined
            ? fxCalc.exceeds_300
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "FCA Account Found",
          fxCalc?.fca_account_found !== undefined
            ? fxCalc.fca_account_found
              ? "Yes"
              : "No"
            : "N/A",
        ],
      ],
    },
    checklist: {
      title: "Checklist Validation",
      rows: [
        [
          "Email Rejection",
          checklist?.payments_team_rejection_email !== undefined
            ? checklist.payments_team_rejection_email
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.email_rejection !== undefined
            ? reportData.flow_checklist.email_rejection
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Correct Payment",
          checklist?.correct_payment_attached !== undefined
            ? checklist.correct_payment_attached
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.correct_payment !== undefined
            ? reportData.flow_checklist.correct_payment
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Has MT103/202",
          checklist?.has_mt103_and_202 !== undefined
            ? checklist.has_mt103_and_202
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.has_mt103_202 !== undefined
            ? reportData.flow_checklist.has_mt103_202
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "AUD Payment",
          checklist?.is_aud_payment !== undefined
            ? checklist.is_aud_payment
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.aud_payment !== undefined
            ? reportData.flow_checklist.aud_payment
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Amendment Sent",
          checklist?.amendment_previously_sent !== undefined
            ? checklist.amendment_previously_sent
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.amendment_sent !== undefined
            ? reportData.flow_checklist.amendment_sent
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "CBA FCA Return",
          checklist?.returned_due_to_cba_fca !== undefined
            ? checklist.returned_due_to_cba_fca
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.cba_fca_return !== undefined
            ? reportData.flow_checklist.cba_fca_return
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "No Funds Due Charges",
          checklist?.no_funds_due_to_charges !== undefined
            ? checklist.no_funds_due_to_charges
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.no_funds_due_charges !== undefined
            ? reportData.flow_checklist.no_funds_due_charges
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Return Reason Clear",
          checklist?.return_reason_clear !== undefined
            ? checklist.return_reason_clear
              ? "Yes"
              : "No"
            : reportData?.flow_checklist?.return_reason_clear !== undefined
            ? reportData.flow_checklist.return_reason_clear
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Manual Review Required",
          reportData?.flow_checklist?.manual_review_required !== undefined
            ? reportData.flow_checklist.manual_review_required
              ? "Yes"
              : "No"
            : checklist?.manual_review_required !== undefined
            ? checklist.manual_review_required
              ? "Yes"
              : "No"
            : "N/A",
        ],
      ],
    },
    nostro: {
      title: "Nostro Reconciliation",
      rows: [
        [
          "Match Found",
          nostroResult?.found !== undefined
            ? nostroResult.found
              ? "Yes"
              : "No"
            : verifierChecks?.nostro_match_found !== undefined
            ? verifierChecks.nostro_match_found
              ? "Yes"
              : "No"
            : verifierSummary?.nostro_match_found !== undefined
            ? verifierSummary.nostro_match_found
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Match Type",
          getValue(
            nostroResult?.match_type,
            verifierChecks?.match_type,
            verifierSummary?.match_type
          ),
        ],
        [
          "Statement ID",
          getValue(
            nostroResult?.nostro_entry?.statement_id,
            verifierChecks?.nostro_entry?.statement_id,
            verifierSummary?.nostro_entry?.statement_id,
            typeof nostroResult?.nostro_entry === "string"
              ? nostroResult.nostro_entry
              : undefined
          ),
        ],
        [
          "Value Date",
          getValue(
            nostroResult?.nostro_entry?.value_date,
            verifierChecks?.nostro_entry?.value_date,
            verifierSummary?.nostro_entry?.value_date
          ),
        ],
        [
          "Currency",
          getValue(
            nostroResult?.nostro_entry?.currency,
            verifierChecks?.nostro_entry?.currency,
            verifierSummary?.nostro_entry?.currency
          ),
        ],
        [
          "Amount",
          getValue(
            nostroResult?.nostro_entry?.amount,
            verifierChecks?.nostro_entry?.amount,
            verifierSummary?.nostro_entry?.amount
          ),
        ],
        [
          "DR/CR",
          getValue(
            nostroResult?.nostro_entry?.dr_cr,
            verifierChecks?.nostro_entry?.dr_cr,
            verifierSummary?.nostro_entry?.dr_cr
          ),
        ],
      ],
    },
    refund: {
      title: "Refund Processing (D1-D9)",
      rows: [
        [
          "Can Process",
          canProcess
            ? "Yes"
            : refundDecision?.can_process !== undefined
            ? refundDecision.can_process
              ? "Yes"
              : "No"
            : reportData?.summary?.can_process !== undefined
            ? reportData.summary.can_process
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Final Action",
          getValue(
            refundDecision?.reason,
            refundDecision?.final_action,
            reportData?.summary?.reason,
            reportData?.refund_processing?.refund_decision?.reason,
            reportData?.refund_flow?.final_decision
          ),
        ],
        [
          "Account Operations",
          String(
            reportData?.refund_processing?.refund_decision?.account_operations
              ?.length ||
              reportData?.account_operations?.length ||
              reportData?.summary?.account_operations_count ||
              0
          ),
        ],
        [
          "Credit Account IBAN",
          getValue(
            refundDecision?.credit_account_iban,
            reportData?.summary?.credit_account_iban,
            reportData?.refund_processing?.refund_decision?.credit_account_iban
          ),
        ],
        [
          "D1 Decision",
          getValue(
            refundDecision?.d1_d9_decisions?.D1?.decision,
            reportData?.refund_processing?.refund_decision?.d1_d9_decisions?.D1
              ?.decision
          ),
        ],
        [
          "D2 Decision",
          getValue(
            refundDecision?.d1_d9_decisions?.D2?.decision,
            reportData?.refund_processing?.refund_decision?.d1_d9_decisions?.D2
              ?.decision
          ),
        ],
        [
          "D3 Decision",
          getValue(
            refundDecision?.d1_d9_decisions?.D3?.decision,
            reportData?.refund_processing?.refund_decision?.d1_d9_decisions?.D3
              ?.decision
          ),
        ],
      ],
    },
    verifier: {
      title: "Verifier Agent",
      rows: [
        [
          "Reconciliation OK",
          verifierSummary?.reconciliation_ok !== undefined
            ? verifierSummary.reconciliation_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.reconciliation_ok !== undefined
            ? reportData.verification.reconciliation_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Sequence OK",
          verifierChecks?.sequence_ok !== undefined
            ? verifierChecks.sequence_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.sequence_ok !== undefined
            ? reportData.verification.sequence_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Cross Checks OK",
          verifierChecks?.cross_checks_ok !== undefined
            ? verifierChecks.cross_checks_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.cross_checks_ok !== undefined
            ? reportData.verification.cross_checks_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "CSV Validation OK",
          verifierChecks?.csv_validation_ok !== undefined
            ? verifierChecks.csv_validation_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.csv_validation_ok !== undefined
            ? reportData.verification.csv_validation_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Sanctions OK",
          verifierChecks?.sanctions_ok !== undefined
            ? verifierChecks.sanctions_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.sanctions_ok !== undefined
            ? reportData.verification.sanctions_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "FX Loss Within Limit",
          verifierChecks?.fx_loss_within_limit !== undefined
            ? verifierChecks.fx_loss_within_limit
              ? "Yes"
              : "No"
            : reportData?.verification?.fx_loss_within_limit !== undefined
            ? reportData.verification.fx_loss_within_limit
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Nostro Match Found",
          verifierChecks?.nostro_match_found !== undefined
            ? verifierChecks.nostro_match_found
              ? "Yes"
              : "No"
            : reportData?.verification?.nostro_match_found !== undefined
            ? reportData.verification.nostro_match_found
              ? "Yes"
              : "No"
            : nostroResult?.found !== undefined
            ? nostroResult.found
              ? "Yes"
              : "No"
            : "N/A",
        ],
        [
          "Process Flow OK",
          verifierChecks?.process_flow_ok !== undefined
            ? verifierChecks.process_flow_ok
              ? "Yes"
              : "No"
            : reportData?.verification?.process_flow_ok !== undefined
            ? reportData.verification.process_flow_ok
              ? "Yes"
              : "No"
            : "N/A",
        ],
      ],
    },
    communications: {
      title: "Communications Agent",
      rows: [
        [
          "Templates Generated",
          String(
            reportData?.communications?.templates_generated ||
              (Array.isArray(commTemplates)
                ? commTemplates.length
                : Object.keys(commTemplates || {}).length) ||
              0
          ),
        ],
        [
          "Customer Notification",
          getValue(
            (commTemplates as any)?.customer_notification?.status,
            reportData?.communications?.customer_notification,
            canProcess ? "SENT" : undefined
          ),
        ],
        [
          "Branch Advisory",
          getValue(
            (commTemplates as any)?.branch_advisory?.status,
            reportData?.communications?.branch_advisory,
            canProcess ? "Prepared" : undefined
          ),
        ],
        [
          "Decision Summary",
          getValue(
            reportData?.communications?.decision_summary,
            reportData?.summary?.reason,
            refundDecision?.reason,
            reportData?.refund_processing?.refund_decision?.reason
          ),
        ],
      ],
    },
  };

  const handleAgentClick = (e: React.MouseEvent, agentKey: string) => {
    e.stopPropagation(); // Prevent event bubbling to parent elements
    const data = agentData[agentKey];
    if (data) {
      setModalData(data);
      setModalVisible(true);
    }
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setModalData(null);
  };

  const handleModalBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleCloseModal();
    }
  };

  return (
    <Card title="Interactive Agent Graph">
      <p className="mb-5 text-gray-600 dark:text-gray-400">
        Click on each agent to see the data flowing through them
      </p>

      {/* Agent Details Modal */}
      {modalVisible && modalData && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={handleModalBackdropClick}
          style={{
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(4px)",
          }}
        >
          <div
            className="bg-white dark:bg-gray-800 border-2 border-yellow-500 rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white px-6 py-4 flex justify-between items-center">
              <h3 className="text-xl font-semibold">{modalData.title}</h3>
              <button
                onClick={handleCloseModal}
                className="text-white hover:text-gray-300 text-2xl font-bold leading-none w-8 h-8 flex items-center justify-center rounded hover:bg-white/10 transition-colors"
                title="Close"
              >
                ×
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto flex-1">
              <div className="space-y-2">
                {modalData.rows.map(([label, value], idx) => (
                  <div
                    key={idx}
                    className="flex flex-col sm:flex-row sm:justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-b-0 gap-2"
                  >
                    <span className="font-semibold text-gray-600 dark:text-gray-400 text-sm">
                      {label}:
                    </span>
                    <span className="text-gray-900 dark:text-white text-sm text-right break-words">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Graph Container */}
      <div className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-5 mt-5 overflow-x-auto">
        <div className="flex items-center gap-5 min-w-[1200px] py-5">
          {/* Logger Agent */}
          <div
            className="bg-white dark:bg-gray-800 border-2 border-yellow-500 rounded-lg min-w-[180px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg hover:border-black"
            onClick={(e) => handleAgentClick(e, "prep_logger")}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">📝</div>
              <div className="mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  Logger Agent
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Data Preparation
                </p>
              </div>
              <div className="text-green-500 text-xl">✓</div>
            </div>
          </div>

          {/* Arrow 1 */}
          <div className="flex items-center justify-center flex-shrink-0">
            <svg width="40" height="20" viewBox="0 0 40 20">
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
                </marker>
              </defs>
              <line
                x1="0"
                y1="10"
                x2="30"
                y2="10"
                stroke="#666"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
            </svg>
          </div>

          {/* Investigation Agent */}
          <div
            className="bg-white dark:bg-gray-800 border-2 border-yellow-500 rounded-lg min-w-[180px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg hover:border-black"
            onClick={(e) => handleAgentClick(e, "investigator")}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">🔍</div>
              <div className="mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  Investigation Agent
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Eligibility & Validation
                </p>
              </div>
              <div className="text-green-500 text-xl">✓</div>
            </div>
          </div>

          {/* Arrow 2 */}
          <div className="flex items-center justify-center flex-shrink-0">
            <svg width="40" height="20" viewBox="0 0 40 20">
              <line
                x1="0"
                y1="10"
                x2="30"
                y2="10"
                stroke="#666"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
            </svg>
          </div>

          {/* Actioning Agent */}
          <div
            className="bg-white dark:bg-gray-800 border-[3px] border-black rounded-lg min-w-[220px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg"
            onClick={(e) => handleAgentClick(e, "actioning")}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">⚙️</div>
              <div className="mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  Actioning Agent
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Processing & Decision
                </p>
              </div>
              <div className="text-green-500 text-xl mb-2">✓</div>
            </div>

            {/* Sub-agents */}
            <div className="flex justify-around px-2 py-3 bg-gray-100 dark:bg-gray-700 border-t border-gray-300 dark:border-gray-600 rounded-b-lg gap-1">
              <div
                className="flex flex-col items-center px-1 py-1.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 cursor-pointer transition-all hover:bg-yellow-500 hover:border-black hover:scale-105 min-w-[40px]"
                onClick={(e) => handleAgentClick(e, "fx")}
              >
                <div className="text-base mb-0.5">💱</div>
                <div className="text-xs text-gray-700 dark:text-gray-300">
                  FX
                </div>
              </div>
              <div
                className="flex flex-col items-center px-1 py-1.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 cursor-pointer transition-all hover:bg-yellow-500 hover:border-black hover:scale-105 min-w-[40px]"
                onClick={(e) => handleAgentClick(e, "checklist")}
              >
                <div className="text-base mb-0.5">✅</div>
                <div className="text-xs text-gray-700 dark:text-gray-300">
                  Checklist
                </div>
              </div>
              <div
                className="flex flex-col items-center px-1 py-1.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 cursor-pointer transition-all hover:bg-yellow-500 hover:border-black hover:scale-105 min-w-[40px]"
                onClick={(e) => handleAgentClick(e, "nostro")}
              >
                <div className="text-base mb-0.5">🏦</div>
                <div className="text-xs text-gray-700 dark:text-gray-300">
                  Nostro
                </div>
              </div>
              <div
                className="flex flex-col items-center px-1 py-1.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 cursor-pointer transition-all hover:bg-yellow-500 hover:border-black hover:scale-105 min-w-[40px]"
                onClick={(e) => handleAgentClick(e, "refund")}
              >
                <div className="text-base mb-0.5">💰</div>
                <div className="text-xs text-gray-700 dark:text-gray-300">
                  Refund
                </div>
              </div>
            </div>
          </div>

          {/* Arrow 3 */}
          <div className="flex items-center justify-center flex-shrink-0">
            <svg width="40" height="20" viewBox="0 0 40 20">
              <line
                x1="0"
                y1="10"
                x2="30"
                y2="10"
                stroke="#666"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
            </svg>
          </div>

          {/* Verifier Agent */}
          <div
            className="bg-white dark:bg-gray-800 border-2 border-yellow-500 rounded-lg min-w-[180px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg hover:border-black"
            onClick={(e) => handleAgentClick(e, "verifier")}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">✅</div>
              <div className="mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  Verifier Agent
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Final Validation
                </p>
              </div>
              <div className="text-green-500 text-xl">✓</div>
            </div>
          </div>

          {/* Arrow 4 */}
          <div className="flex items-center justify-center flex-shrink-0">
            <svg width="40" height="20" viewBox="0 0 40 20">
              <line
                x1="0"
                y1="10"
                x2="30"
                y2="10"
                stroke="#666"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
            </svg>
          </div>

          {/* Communications Agent */}
          <div
            className="bg-white dark:bg-gray-800 border-2 border-yellow-500 rounded-lg min-w-[180px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg hover:border-black"
            onClick={(e) => handleAgentClick(e, "communications")}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">📧</div>
              <div className="mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  Communications Agent
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Notifications
                </p>
              </div>
              <div className="text-green-500 text-xl">✓</div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

const CommunicationTab: React.FC<{ reportData: ReportData }> = ({
  reportData,
}) => {
  const commTemplates =
    reportData?.communications?.communication_templates || {};
  const templatesArray = Array.isArray(commTemplates)
    ? commTemplates
    : Object.values(commTemplates);
  const emailPayload =
    reportData?.prep_logger?.email_payload ||
    reportData?.communications?.email_payload;

  // Customer notification email data
  const p004 = reportData?.parsed_data?.pacs004 || {};
  const p008 = reportData?.parsed_data?.pacs008 || {};
  const eligibility = reportData?.investigation?.eligibility || {};
  const csvValidation = reportData?.investigation?.csv_validation || {};
  const customerRecord = csvValidation?.customer || {};
  const refundDecision =
    reportData?.refund_processing?.refund_decision ||
    reportData?.refund_decision ||
    {};
  const canProcess =
    refundDecision?.can_process || reportData?.summary?.can_process || false;

  // Email recipient information
  const initialCustomerNotification =
    (commTemplates as any)?.customer_notification || {};
  const toEmail =
    initialCustomerNotification?.email ||
    customerRecord?.email ||
    "customer@example.com";
  const toName =
    initialCustomerNotification?.recipient ||
    customerRecord?.account_holder_name ||
    customerRecord?.customer_name ||
    p008?.dbtr_name ||
    "Customer";

  // Transaction details
  const uetr = p004?.uetr || reportData?.uetr || "N/A";
  const rtrCcy = p004?.rtr_ccy || "N/A";
  const rtrAmt = p004?.rtr_amount || "N/A";
  const rsnCode = eligibility?.reason || p004?.rsn || "";
  const rsnInfo = p004?.rsn_info || eligibility?.reason_info || "";

  // Reason label mapping
  const reasonLabelMap: Record<string, string> = {
    AC01: "Incorrect Account Number",
    AC04: "Account Closed",
    MS03: "Reason Not Specified",
    CURR: "Wrong Currency",
  };
  const reasonLabel = rsnInfo || reasonLabelMap[rsnCode] || rsnCode || "N/A";

  // FX Loss
  const fxLossAud =
    reportData?.fx_calculation?.loss_aud ||
    eligibility?.fx_loss_aud ||
    reportData?.fx_calculation?.fx_loss_aud ||
    0;
  const fxLossDisplay =
    fxLossAud != null ? `AUD ${fxLossAud.toFixed(2)}` : "N/A";

  // Status
  const statusText = canProcess ? "Refund Processed" : "Refund Pending";

  // Action required text
  const needsAlt = (rsnCode === "AC01" || rsnCode === "AC04") && !canProcess;
  const actionText = needsAlt
    ? "Our systems indicate the original IBAN is no longer valid. To proceed with the refund, please provide an alternate active account number."
    : rsnCode === "CURR"
    ? "This case requires manual review due to currency mismatch."
    : !canProcess
    ? "We are reviewing your case and will update you shortly."
    : "No action required.";

  // State for Gemini-generated email
  const [emailContent, setEmailContent] = useState<{
    subject: string;
    body: string;
    html_body: string;
    generated_by?: "gemini" | "template";
  }>(() => {
    // Initialize with Gemini-generated email if available, otherwise use defaults
    const customerNotif = initialCustomerNotification;
    // Check if we have valid email content (non-empty strings)
    const hasHtmlBody =
      customerNotif?.html_body && customerNotif.html_body.trim().length > 0;
    const hasBody = customerNotif?.body && customerNotif.body.trim().length > 0;
    const hasSubject =
      customerNotif?.subject && customerNotif.subject.trim().length > 0;

    if (hasHtmlBody || hasBody || hasSubject) {
      console.log(
        "DEBUG: Initializing email content from customer_notification",
        {
          hasHtmlBody,
          hasBody,
          hasSubject,
          generated_by: customerNotif?.generated_by,
        }
      );
      return {
        subject:
          customerNotif?.subject ||
          `Refund Status – Action Required for Transaction UETR ${uetr}`,
        body: customerNotif?.body || "",
        html_body: customerNotif?.html_body || "",
        generated_by: customerNotif?.generated_by || "template",
      };
    }
    console.log("DEBUG: No valid email content found, using default template");
    return {
      subject: `Refund Status – Action Required for Transaction UETR ${uetr}`,
      body: "",
      html_body: "",
      generated_by: "template",
    };
  });

  // Update email content when reportData changes (e.g., when switching reports)
  useEffect(() => {
    const customerNotif = initialCustomerNotification;
    // Check if we have valid email content (non-empty strings)
    const hasHtmlBody =
      customerNotif?.html_body && customerNotif.html_body.trim().length > 0;
    const hasBody = customerNotif?.body && customerNotif.body.trim().length > 0;
    const hasSubject =
      customerNotif?.subject && customerNotif.subject.trim().length > 0;

    if (hasHtmlBody || hasBody || hasSubject) {
      console.log("DEBUG: Setting email content from customer_notification", {
        hasHtmlBody,
        hasBody,
        hasSubject,
        generated_by: customerNotif?.generated_by,
        html_body_length: customerNotif?.html_body?.length || 0,
      });
      setEmailContent({
        subject:
          customerNotif?.subject ||
          `Refund Status – Action Required for Transaction UETR ${uetr}`,
        body: customerNotif?.body || "",
        html_body: customerNotif?.html_body || "",
        generated_by: customerNotif?.generated_by || "template",
      });
    } else {
      console.log(
        "DEBUG: No valid email content found in customer_notification",
        {
          customerNotif,
          hasHtmlBody,
          hasBody,
          hasSubject,
        }
      );
    }
  }, [reportData?.run_id, initialCustomerNotification, uetr]);

  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenerateStatus, setRegenerateStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  // Get run_id for regeneration
  const runId = reportData?.run_id || reportData?.transaction_id || "";

  // Handle regenerate email
  const handleRegenerateEmail = async () => {
    if (!runId) {
      setRegenerateStatus({
        type: "error",
        message: "Could not determine run_id. Please refresh the page.",
      });
      return;
    }

    setIsRegenerating(true);
    setRegenerateStatus(null);

    try {
      const response = await apiService.regenerateEmail(runId);
      if (response.success && response.email) {
        setEmailContent({
          subject: response.email.subject,
          body: response.email.body,
          html_body: response.email.html_body,
          generated_by: response.email.generated_by,
        });
        setRegenerateStatus({
          type: "success",
          message: "✅ Email regenerated successfully!",
        });
        // Clear success message after 3 seconds
        setTimeout(() => setRegenerateStatus(null), 3000);
      } else {
        throw new Error(response.error || "Failed to regenerate email");
      }
    } catch (error) {
      console.error("Error regenerating email:", error);
      setRegenerateStatus({
        type: "error",
        message: `❌ Error: ${
          error instanceof Error
            ? error.message
            : "Failed to regenerate email. Please try again."
        }`,
      });
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Customer Notification Email */}
      <Card title="Customer Notification Email">
        <div className="flex justify-between items-center mb-4">
          <div className="flex-1"></div>
          <button
            onClick={handleRegenerateEmail}
            disabled={isRegenerating || !runId}
            className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-black font-semibold rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            {isRegenerating ? (
              <>
                <span className="animate-spin">⏳</span>
                Regenerating...
              </>
            ) : (
              <>🔄 Regenerate Mail</>
            )}
          </button>
        </div>

        {regenerateStatus && (
          <div
            className={`mb-4 p-3 rounded-lg ${
              regenerateStatus.type === "success"
                ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200"
                : "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200"
            }`}
          >
            {regenerateStatus.message}
          </div>
        )}

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          {/* Email Header */}
          <div className="bg-gradient-to-r from-yellow-50 to-white dark:from-yellow-900/20 dark:to-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-[90px_1fr] gap-x-3 gap-y-2 text-sm text-gray-900 dark:text-gray-100">
              <div className="font-semibold">To:</div>
              <div>
                {toName} &lt;{toEmail}&gt;
              </div>
              <div className="font-semibold">From:</div>
              <div>refunds@cba.com.au</div>
              <div className="font-semibold">Subject:</div>
              <div id="email-subject">{emailContent.subject}</div>
            </div>
            {emailContent.generated_by === "gemini" && (
              <div className="mt-2">
                <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                  ✨ Generated by Gemini AI
                </span>
              </div>
            )}
          </div>

          {/* Email Body */}
          <div
            id="email-body"
            className="p-4 text-gray-800 dark:text-gray-200 leading-relaxed"
          >
            {emailContent.html_body ? (
              <div
                dangerouslySetInnerHTML={{ __html: emailContent.html_body }}
              />
            ) : emailContent.body ? (
              <pre className="whitespace-pre-wrap font-sans">
                {emailContent.body}
              </pre>
            ) : (
              // Fallback to static template
              <>
                <p className="mb-3">Dear {toName},</p>
                <p className="mb-3">
                  We've reviewed your payment return request with UETR{" "}
                  <strong>{uetr}</strong> and found the following:
                </p>
                <ul className="list-disc list-inside mb-4 ml-4 space-y-1">
                  <li>
                    <strong>Return Amount</strong>: {rtrCcy} {rtrAmt}
                  </li>
                  <li>
                    <strong>Reason</strong>: {reasonLabel}
                    {rsnCode ? ` (${rsnCode})` : ""}
                  </li>
                  <li>
                    <strong>FX Loss</strong>: {fxLossDisplay}
                  </li>
                  <li>
                    <strong>Status</strong>: {statusText}
                  </li>
                </ul>

                <div className="my-4 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200">
                  <div className="font-bold mb-1">Action Required</div>
                  <div>{actionText}</div>
                </div>

                <p className="mb-3">
                  If you have any questions or need support, please contact your
                  relationship manager or reply to this email.
                </p>
                <p>
                  Sincerely,
                  <br />
                  <strong>CBA Refund Investigations Team</strong>
                </p>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Communication Templates Summary */}
      <Card title="Communication Templates">
        <div className="grid md:grid-cols-2 gap-x-8 gap-y-2">
          <InfoItem label="Templates Generated" value={templatesArray.length} />
          <InfoItem
            label="Customer Notification"
            value={
              (commTemplates as any)?.customer_notification?.status ||
              (canProcess ? "SENT" : "N/A")
            }
          />
          <InfoItem
            label="Branch Advisory"
            value={
              (commTemplates as any)?.branch_advisory?.status ||
              (canProcess ? "Prepared" : "N/A")
            }
          />
          <InfoItem
            label="Ops Advisory Priority"
            value={(commTemplates as any)?.ops_advisory?.priority || "Normal"}
          />
        </div>
        {templatesArray.length > 0 && (
          <div className="mt-4 space-y-4">
            {templatesArray.map((template: any, idx: number) => (
              <div
                key={idx}
                className="p-4 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <div className="font-semibold mb-2">
                  {template.type || `Template ${idx + 1}`}
                </div>
                {template.subject && (
                  <div className="text-sm mb-1">
                    <strong>Subject:</strong> {template.subject}
                  </div>
                )}
                {template.priority && (
                  <div className="text-sm mb-1">
                    <strong>Priority:</strong> {template.priority}
                  </div>
                )}
                {template.body && (
                  <div className="text-sm mt-2">
                    <strong>Body:</strong>
                    <pre className="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-auto max-h-48">
                      {template.body}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* MT103 Email (if available) */}
      {emailPayload?.body && (
        <Card title="MT103 Email (Intelli Processing)">
          <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded p-4">
            <div className="mb-4 space-y-2 text-sm">
              <div>
                <strong>From:</strong> CBA Refund System
                &lt;refunds@cba.com.au&gt;
              </div>
              <div>
                <strong>To:</strong>{" "}
                {reportData?.prep_logger?.email_recipient ||
                  reportData?.communications?.email_recipient ||
                  "Intelli Processing"}
              </div>
              <div>
                <strong>Subject:</strong>{" "}
                {emailPayload?.subject || "return of funds"}
              </div>
              {emailPayload?.reference && (
                <div>
                  <strong>Reference:</strong> {emailPayload.reference}
                </div>
              )}
            </div>
            <pre className="text-xs font-mono text-gray-900 dark:text-white whitespace-pre-wrap overflow-x-auto max-h-96">
              {emailPayload.body}
            </pre>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Report;
