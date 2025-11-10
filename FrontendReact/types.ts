export interface Case {
  case_id: string;
  description: string;
  amount: string;
  currency: string;
  status: "generated" | "processing" | "completed" | "failed";
  created_at: string;
  run_id?: string;
  email_subject?: string;
  email_recipient?: string;
  email_body?: string;
}

export interface EmailPreview {
  index: number;
  pacs004_filename: string;
  pacs008_filename: string;
  debtor_name: string;
  amount: string;
  currency: string;
  email_subject: string;
  email_recipient: string;
  email_body: string;
  pacs004_content: string;
  pacs008_content: string;
}

export interface ReportData {
  run_id: string;
  timestamp: string;
  transaction_id: string;
  uetr: string;
  case_id?: string;
  prep_logger?: {
    case_id?: string;
    email_payload?: {
      subject: string;
      body: string;
      reference: string;
    };
    email_recipient?: string;
    processing_timestamp?: string;
  };
  investigation?: {
    summary: {
      uetr?: string;
      e2e_id?: string;
      customer_account?: string;
      return_reason?: string;
      return_reason_info?: string;
      auto_refund_eligible?: boolean;
      customer_valid?: boolean;
      cross_checks?: string;
      currency_mismatch?: boolean;
    };
  };
  verification?: {
    verifier_summary?: {
      checks?: {
        nostro_match_found?: boolean;
        match_type?: string;
        nostro_entry?: string;
      };
    };
    reconciliation_ok?: boolean;
    sequence_ok?: boolean;
    cross_checks_ok?: boolean;
    csv_validation_ok?: boolean;
    non_branch_ok?: boolean;
    sanctions_ok?: boolean;
    fx_loss_within_limit?: boolean;
    nostro_match_found?: boolean;
    process_flow_ok?: boolean;
    decision?: string;
    decision_reason?: string;
  };
  communications?: {
    email_payload?: {
      subject?: string;
      body?: string;
      to?: string;
      from?: string;
    };
    email_recipient?: string;
    templates_generated?: number;
    customer_notification?: {
      recipient?: string;
      email?: string;
      subject?: string;
      body?: string;
      html_body?: string;
      status?: string;
      generated_by?: "gemini" | "template";
    };
    branch_advisory?: string;
    ops_advisory_priority?: string;
    decision_summary?: string;
  };
  fx_calculation?: {
    original_amount?: number;
    returned_amount?: number;
    original_aud?: number;
    returned_aud?: number;
    fx_loss_aud?: number;
    exceeds_300?: boolean;
    fca_account_found?: boolean;
    calculation_method?: string;
  };
  flow_checklist?: {
    email_rejection?: boolean;
    correct_payment?: boolean;
    has_mt103_202?: boolean;
    aud_payment?: boolean;
    amendment_sent?: boolean;
    cba_fca_return?: boolean;
    no_funds_due_charges?: boolean;
    return_reason_clear?: boolean;
    manual_review_required?: boolean;
  };
  account_operations?: Array<{
    operation_type: "DEBIT" | "CREDIT";
    account_name?: string;
    account_iban: string;
    account_type?: string;
    amount: number;
    currency: string;
    balance_before: number;
    balance_after: number;
    reference?: string;
  }>;
  refund_decision?: {
    can_process?: boolean;
    final_action?: string;
    credit_account_iban?: string;
  };
  summary?: {
    can_process?: boolean;
    reason?: string;
    final_status?: string;
    pending_until?: string;
    case_type?: string;
    refund_status?: string;
    case_status?: string;
    case_closure_status?: string;
    next_actions?: string;
  };
}

export interface ReportSummary {
  run_id: string;
  timestamp: string;
  transaction_id: string;
  can_process: boolean;
  reason: string;
}

export interface ProcessCasesResponse {
  success: boolean;
  message: string;
  processed_cases?: Array<{
    case_id: string;
    run_id: string;
    status: "completed";
    result: {
      run_id: string;
      success: boolean;
      timestamp: string;
    };
  }>;
  failed_cases?: Array<{
    case_id: string;
    status: "failed";
    error: string;
  }>;
}

export interface EmailPreviewResponse {
  success: boolean;
  message: string;
  email_previews?: EmailPreview[];
}

export interface CreateCasesResponse {
  success: boolean;
  message: string;
  cases?: Case[];
}

export interface PacsPair {
  id: string;
  pacs004_filename: string;
  pacs008_filename: string;
  pacs004_path: string;
  pacs008_path: string;
  debtor_name: string;
  amount: string;
  currency: string;
  display_name: string;
}

export interface PacsPairsResponse {
  pairs: PacsPair[];
}

export interface CreateCaseFromFilesResponse {
  success: boolean;
  message: string;
  case?: Case;
  is_duplicate?: boolean;
  existing_case_id?: string;
}

export interface RegenerateEmailResponse {
  success: boolean;
  email?: {
    subject: string;
    body: string;
    html_body: string;
    generated_by: "gemini" | "template";
  };
  error?: string;
}
