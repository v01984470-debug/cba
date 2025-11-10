nodes:
  - id: start
    type: start
    description: "Begin the refund decision flow."

  - id: review_payment_details
    type: tool
    description: "Open the pacs.004/pacs.008 XML and review all payment details."

  - id: email_rejection_check
    type: decision
    question: "Have we received an email from the payments team advising rejection?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: correct_payment_check

  - id: correct_payment_check
    type: decision
    question: "Correct payment attached?"
    branches:
      - condition: "Yes"
        next: has_mt103_and_202
      - condition: "No"
        next: refund_process

  - id: has_mt103_and_202
    type: decision
    question: "Payment has MT103 and MT202?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: is_aud_payment

  - id: is_aud_payment
    type: decision
    question: "Is payment an AUD payment?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: amendment_sent_check

  - id: amendment_sent_check
    type: decision
    question: "Has an amendment been previously sent?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: returned_to_cba_fca

  - id: returned_to_cba_fca
    type: decision
    question: "Was payment returned because the recipient account quoted is a CBA FCA?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: no_funds_due_to_charges

  - id: no_funds_due_to_charges
    type: decision
    question: "Has the overseas bank advised that no funds are to be returned due to charges?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: reason_clear_check

  - id: reason_clear_check
    type: decision
    question: "Is the return reason clear?"
    branches:
      - condition: "Yes"
        next: is_markets_check
      - condition: "No"
        next: refund_process

  - id: is_markets_check
    type: decision
    question: "Is Markets involved?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: remitter_closed_check

  - id: remitter_closed_check
    type: decision
    question: "Is the remitter account closed?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: value_date_check

  - id: value_date_check
    type: decision
    question: "Payment returned due to Value Date?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: iban_invalid_check

  - id: iban_invalid_check
    type: decision
    question: "OFI advised IBAN format is invalid?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: internal_policy_check

  - id: internal_policy_check
    type: decision
    question: "Reason: Internal policy?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: correspondent_issue_check

  - id: correspondent_issue_check
    type: decision
    question: "Reason: Correspondent issue?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: wrong_currency_check

  - id: wrong_currency_check
    type: decision
    question: "Reason: Wrong Currency?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: client_amending_instructions_check

  - id: client_amending_instructions_check
    type: decision
    question: "Has the client provided amending instructions to resend?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: calculate_loss

  - id: calculate_loss
    type: payment_system
    description: "Calculate current loss at today's prevailing rate."
    next: loss_threshold_check

  - id: loss_threshold_check
    type: decision
    question: "Is the loss amount greater than $300?"
    branches:
      - condition: "Yes"
        next: refund_process
      - condition: "No"
        next: refund_process

  - id: refund_process
    type: end
    description: "Execute Refund Process as defined in refund_flow_.md"
