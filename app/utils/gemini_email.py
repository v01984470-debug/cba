"""
Gemini API integration for dynamic email generation.
Generates customer notification emails while preserving backend data integrity.
"""
import os
import json
import re
import html as html_escape
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Email generation will use fallback templates.")


def initialize_gemini() -> bool:
    """Initialize Gemini API with credentials from environment."""
    if not GEMINI_AVAILABLE:
        return False

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        return False

    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error initializing Gemini API: {e}")
        return False


def generate_customer_email(
    recipient_name: str,
    recipient_email: str,
    uetr: str,
    return_amount: str,
    return_currency: str,
    reason_code: str,
    reason_info: str,
    fx_loss_aud: Optional[float],
    status: str,
    action_required: str,
    variation_mode: bool = False
) -> Dict[str, str]:
    """
    Generate customer notification email using Gemini API.

    Args:
        recipient_name: Customer's name
        recipient_email: Customer's email address
        uetr: Unique End-to-End Transaction Reference
        return_amount: Return amount
        return_currency: Return currency code
        reason_code: Return reason code (e.g., AC01, AC04)
        reason_info: Return reason description
        fx_loss_aud: FX loss in AUD (optional)
        status: Refund status (e.g., "Refund Processed", "Refund Pending")
        action_required: Action required message
        variation_mode: If True, request varied wording while maintaining consistency

    Returns:
        Dictionary with 'subject', 'body', and 'html_body' keys
    """
    if not GEMINI_AVAILABLE or not initialize_gemini():
        # Fallback to template-based email
        return _generate_fallback_email(
            recipient_name, uetr, return_amount, return_currency,
            reason_code, reason_info, fx_loss_aud, status, action_required
        )

    try:
        # Build the prompt with strict data preservation instructions
        variation_instruction = (
            "Use varied phrasing and layout while maintaining the exact same meaning, "
            "tone, and all data values." if variation_mode else ""
        )

        prompt = f"""Generate a professional customer notification email for a payment refund investigation.

REQUIREMENTS:
- Use professional, courteous tone appropriate for banking communications
- Preserve ALL data values exactly as provided below - do not modify or interpret them
- Maintain consistent message intent and tone
- Use markdown formatting for better readability:
  * Use **bold** for field labels (e.g., **UETR:**, **Return Amount:**)
  * Use bullet points (*) for transaction details list
  * Use **Action Required:** as a bold header for action sections
{variation_instruction}

DATA TO INCLUDE (use these values exactly):
- Recipient Name: {recipient_name}
- UETR: {uetr}
- Return Amount: {return_currency} {return_amount}
- Return Reason: {reason_info} ({reason_code if reason_code else 'N/A'})
- FX Loss: {'AUD ' + format(fx_loss_aud, '.2f') if fx_loss_aud is not None else 'N/A'}
- Status: {status}
- Action Required: {action_required}

EMAIL STRUCTURE:
1. Professional greeting addressing the customer by name
2. Brief explanation of the refund investigation
3. Transaction details in a bulleted list format with bold labels:
   * **UETR:** [value]
   * **Return Amount:** [value]
   * **Return Reason:** [value]
   * **FX Loss:** [value]
   * **Status:** [value]
4. Action required section with **Action Required:** as bold header (if applicable)
5. Closing with contact information offer
6. Professional signature: "CBA Refund Investigations Team"

FORMATTING GUIDELINES:
- Use **text** for bold formatting (field labels, headers)
- Use * at the start of lines for bullet points
- Ensure all numerical values, codes, and references are included exactly as provided
- Use proper line breaks between sections"""

        # Generate content using Gemini
        # Get model name from environment variable, with fallbacks
        env_model = os.getenv("MODEL", "").strip()

        # Build list of models to try (user's model first, then fallbacks)
        model_names = []
        if env_model:
            # Handle both formats: "gemini/gemini-2.5-flash-lite" and "gemini-2.5-flash-lite"
            clean_model = env_model.replace("gemini/", "").strip()
            model_names.append(clean_model)
            # Also try with gemini/ prefix if it wasn't there
            if not env_model.startswith("gemini/"):
                model_names.append(f"gemini/{clean_model}")

        # Add fallback models
        model_names.extend(
            ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'])

        # Remove duplicates while preserving order
        seen = set()
        model_names = [m for m in model_names if not (
            m in seen or seen.add(m))]

        model = None
        response = None
        last_error = None

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                # If we get here, the model worked
                print(f"Successfully using Gemini model: {model_name}")
                break
            except Exception as e:
                error_msg = str(e)
                last_error = e
                # If it's a 404 or model not found, try next model
                if '404' in error_msg or 'not found' in error_msg.lower() or 'not supported' in error_msg.lower():
                    print(f"Model {model_name} not available, trying next...")
                    continue
                else:
                    # For other errors, re-raise
                    print(f"Error with model {model_name}: {error_msg}")
                    raise

        if not response:
            error_detail = f"Last error: {str(last_error)}" if last_error else "No models available"
            raise Exception(
                f"None of the available models ({', '.join(model_names)}) could be used. {error_detail}")

        email_body = response.text.strip()

        # Remove subject line if it was included in the body (some models include it)
        # Check if the body starts with "Subject:" and remove that line
        if email_body.startswith("Subject:"):
            lines = email_body.split('\n', 1)
            if len(lines) > 1:
                email_body = lines[1].strip()

        # Also check for subject in the first few lines
        lines = email_body.split('\n')
        if len(lines) > 0 and lines[0].strip().startswith("Subject:"):
            email_body = '\n'.join(lines[1:]).strip()

        # Note: We'll convert markdown to HTML in _convert_to_html
        # This preserves formatting like **bold** and converts them to <strong> tags

        # Generate subject line using the same model
        subject_prompt = f"""Generate a concise, professional email subject line for a refund investigation notification.

Context:
- Customer: {recipient_name}
- UETR: {uetr}
- Status: {status}

Generate only the subject line as plain text (no "Subject:" prefix, no markdown, no quotes, max 80 characters)."""

        try:
            subject_response = model.generate_content(subject_prompt)
            subject = subject_response.text.strip().replace('Subject:', '').strip()
        except Exception:
            # Fallback subject if generation fails
            subject = f"Refund Status – Action Required for Transaction UETR {uetr}"

        # Clean markdown from subject and remove quotes
        subject = _clean_markdown(subject)
        subject = subject.strip('"\'')
        if len(subject) > 80:
            subject = f"Refund Status – Action Required for Transaction UETR {uetr}"

        # Convert plain text body to HTML for better display
        # Always convert to HTML (we cleaned markdown, so it should be plain text now)
        html_body = _convert_to_html(
            email_body, recipient_name, recipient_email, uetr)

        # Ensure html_body is not empty
        if not html_body or not html_body.strip():
            print(f"Warning: HTML body is empty after conversion, using plain text body")
            # Fallback: wrap plain text in basic HTML
            html_body = f"<p>{html_escape.escape(email_body).replace(chr(10), '<br>')}</p>"

        return {
            "subject": subject,
            "body": email_body,
            "html_body": html_body,
            "generated_by": "gemini"
        }

    except Exception as e:
        print(f"Error generating email with Gemini API: {e}")
        # Fallback to template-based email
        return _generate_fallback_email(
            recipient_name, uetr, return_amount, return_currency,
            reason_code, reason_info, fx_loss_aud, status, action_required
        )


def _generate_fallback_email(
    recipient_name: str,
    uetr: str,
    return_amount: str,
    return_currency: str,
    reason_code: str,
    reason_info: str,
    fx_loss_aud: Optional[float],
    status: str,
    action_required: str
) -> Dict[str, str]:
    """Generate fallback email template when Gemini API is unavailable."""
    fx_loss_display = f"AUD {fx_loss_aud:.2f}" if fx_loss_aud is not None else "N/A"

    body = f"""Dear {recipient_name},

We've reviewed your payment return request with UETR {uetr} and found the following:

• Return Amount: {return_currency} {return_amount}
• Reason: {reason_info} ({reason_code if reason_code else 'N/A'})
• FX Loss: {fx_loss_display}
• Status: {status}

Action Required
{action_required}

If you have any questions or need support, please contact your relationship manager or reply to this email.

Sincerely,
CBA Refund Investigations Team"""

    subject = f"Refund Status – Action Required for Transaction UETR {uetr}"

    html_body = _convert_to_html(body, recipient_name, "", uetr)

    return {
        "subject": subject,
        "body": body,
        "html_body": html_body,
        "generated_by": "template"
    }


def _clean_markdown(text: str) -> str:
    """Remove markdown formatting symbols from text and convert to plain text."""
    if not text:
        return text

    # Remove markdown bold (**text** or __text__) - keep the text, we'll handle bold in HTML conversion
    # For now, just remove the markers but preserve the text content
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)

    # Remove markdown italic (*text* or _text_) - keep the text
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)', r'\1', text)

    # Remove markdown code blocks (`text`)
    text = re.sub(r'`([^`]+?)`', r'\1', text)

    # Remove markdown headers (# Header)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # Handle markdown lists - convert to plain text with line breaks
    # Bullet lists (* item, - item, + item) - remove markers but keep text
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Numbered lists (1. item, 2. item) - remove markers but keep text
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)

    return text.strip()


def _convert_markdown_to_html(text: str) -> str:
    """Convert markdown-formatted text to HTML, preserving formatting."""
    # Handle bold text (**text** or __text__) - non-greedy match
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+?)__', r'<strong>\1</strong>', text)

    # Handle italic text (*text* or _text_) - but avoid conflicts with bold
    # Only match single * if not part of **
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'<em>\1</em>', text)

    # Handle inline code (`text`)
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)

    # Convert markdown list items (* item, - item) to HTML list items
    # But we'll handle this in the paragraph processing to preserve structure

    return text


def _convert_to_html(
    plain_text: str,
    recipient_name: str,
    recipient_email: str,
    uetr: str
) -> str:
    """Convert plain text email to HTML format, handling markdown-like formatting."""
    # Split into lines first to identify list items before markdown conversion
    lines = plain_text.split('\n')
    html_paragraphs = []
    current_paragraph = []
    current_list_items = []
    in_action_section = False
    action_lines = []

    for line in lines:
        line_stripped = line.strip()

        # Check if this is a list item (starts with *, -, +, or number) BEFORE markdown conversion
        is_list_item = bool(
            re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line))

        # Skip empty lines (they separate paragraphs/lists)
        if not line_stripped:
            # Finish current list if any
            if current_list_items:
                # Convert markdown in each list item, then escape
                list_items_html = []
                for item in current_list_items:
                    # Convert markdown to HTML first
                    item_html = _convert_markdown_to_html(item)
                    # Then escape while preserving HTML tags
                    item_html = _escape_html_preserve_tags(item_html)
                    list_items_html.append(f'<li>{item_html}</li>')
                list_html = '<ul>' + ''.join(list_items_html) + '</ul>'
                html_paragraphs.append(list_html)
                current_list_items = []

            # Finish current paragraph if any
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                # Convert markdown to HTML, then escape
                para_text = _convert_markdown_to_html(para_text)
                para_text = _escape_html_preserve_tags(para_text)
                html_paragraphs.append(f'<p>{para_text}</p>')
                current_paragraph = []
            continue

        # Handle list items - extract content BEFORE markdown conversion
        if is_list_item:
            # Finish any current paragraph
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                para_text = _convert_markdown_to_html(para_text)
                para_text = _escape_html_preserve_tags(para_text)
                html_paragraphs.append(f'<p>{para_text}</p>')
                current_paragraph = []

            # Remove list marker and add to list (content will be converted to HTML later)
            list_content = re.sub(r'^\s*[-*+]\s+', '', line_stripped)
            list_content = re.sub(r'^\s*\d+\.\s+', '', list_content)
            current_list_items.append(list_content)
            continue
        else:
            # If we were in a list, finish it
            if current_list_items:
                list_items_html = []
                for item in current_list_items:
                    item_html = _convert_markdown_to_html(item)
                    item_html = _escape_html_preserve_tags(item_html)
                    list_items_html.append(f'<li>{item_html}</li>')
                list_html = '<ul>' + ''.join(list_items_html) + '</ul>'
                html_paragraphs.append(list_html)
                current_list_items = []

        # Check for "Action Required" section (before markdown conversion)
        # Check the original line for "Action Required" pattern
        if re.search(r'Action Required', line, re.IGNORECASE):
            # Finish any current paragraph
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                para_text = _convert_markdown_to_html(para_text)
                para_text = _escape_html_preserve_tags(para_text)
                html_paragraphs.append(f'<p>{para_text}</p>')
                current_paragraph = []

            in_action_section = True
            # Extract action header - remove "Action Required:" or "**Action Required:**" etc.
            # Remove markdown bold markers first, then extract the header
            action_header = re.sub(
                r'\*\*Action Required:\*\*', '', line_stripped, flags=re.IGNORECASE)
            action_header = re.sub(r'Action Required:',
                                   '', action_header, flags=re.IGNORECASE)
            action_header = action_header.strip()
            # Convert markdown to HTML for the header
            action_header = _convert_markdown_to_html(action_header)
            action_header = _escape_html_preserve_tags(action_header)
            # Use "Action Required" as header if nothing was extracted
            if not action_header:
                action_header = "Action Required"
            action_lines = [
                f'<div style="font-weight:700;margin-bottom:4px">{action_header}</div>']
            continue

        # Check if we're ending action section (signature or closing)
        if in_action_section and (line_stripped.startswith('Sincerely') or line_stripped.startswith('Best regards') or line_stripped.startswith('CBA Refund')):
            # Close action section
            if action_lines:
                action_html = ''.join(action_lines)
                html_paragraphs.append(
                    f'<div style="margin:14px 0;padding:12px 14px;border-radius:10px;background:#fff3cd;border:1px solid #ffe69c;color:#7a5b00">{action_html}</div>'
                )
                action_lines = []
            in_action_section = False

        # Add line to appropriate section
        if in_action_section:
            escaped_line = _convert_markdown_to_html(line_stripped)
            escaped_line = _escape_html_preserve_tags(escaped_line)
            action_lines.append(f'<div>{escaped_line}</div>')
        else:
            current_paragraph.append(line_stripped)

    # Finish any remaining list
    if current_list_items:
        list_items_html = []
        for item in current_list_items:
            item_html = _convert_markdown_to_html(item)
            item_html = _escape_html_preserve_tags(item_html)
            list_items_html.append(f'<li>{item_html}</li>')
        list_html = '<ul>' + ''.join(list_items_html) + '</ul>'
        html_paragraphs.append(list_html)
        current_list_items = []

    # Finish any remaining paragraph
    if current_paragraph:
        para_text = ' '.join(current_paragraph)
        para_text = _convert_markdown_to_html(para_text)
        para_text = _escape_html_preserve_tags(para_text)
        html_paragraphs.append(f'<p>{para_text}</p>')

    # Finish any remaining action section
    if action_lines:
        action_html = ''.join(action_lines)
        html_paragraphs.append(
            f'<div style="margin:14px 0;padding:12px 14px;border-radius:10px;background:#fff3cd;border:1px solid #ffe69c;color:#7a5b00">{action_html}</div>'
        )

    # If no paragraphs were created, create a simple one
    if not html_paragraphs:
        converted_text = _convert_markdown_to_html(plain_text)
        escaped_text = _escape_html_preserve_tags(converted_text)
        html_paragraphs.append(
            f'<p>{escaped_text.replace(chr(10), "<br>")}</p>')

    return ''.join(html_paragraphs)


def _escape_html_preserve_tags(text: str) -> str:
    """Escape HTML special characters but preserve HTML tags we added (like <strong>, <em>, etc.)."""
    # First, protect our HTML tags
    protected_tags = {
        '<strong>': '___STRONG_OPEN___',
        '</strong>': '___STRONG_CLOSE___',
        '<em>': '___EM_OPEN___',
        '</em>': '___EM_CLOSE___',
        '<code>': '___CODE_OPEN___',
        '</code>': '___CODE_CLOSE___',
    }

    # Replace tags with placeholders
    for tag, placeholder in protected_tags.items():
        text = text.replace(tag, placeholder)

    # Escape HTML
    text = html_escape.escape(text)

    # Restore tags
    reverse_map = {v: k for k, v in protected_tags.items()}
    for placeholder, tag in reverse_map.items():
        text = text.replace(placeholder, tag)

    return text
