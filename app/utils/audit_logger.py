"""
Audit Logger System
Comprehensive audit logging for refund processing operations.
"""

import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events."""
    DECISION = "DECISION"
    ACTION = "ACTION"
    CSV_OPERATION = "CSV_OPERATION"
    DEBIT_AUTHORITY = "DEBIT_AUTHORITY"
    RECONCILIATION = "RECONCILIATION"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"


class AuditLevel(Enum):
    """Audit levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEvent:
    """Audit event structure."""
    event_id: str
    timestamp: str
    event_type: AuditEventType
    level: AuditLevel
    operation: str
    details: Dict[str, Any]
    user: str = "SYSTEM"
    session_id: Optional[str] = None
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = None


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.audit_file = f"{data_dir}/audit_log.csv"
        self.session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.events: List[AuditEvent] = []

    def log_decision(self, node: str, decision: bool, reason: str, next_node: Optional[str] = None,
                     transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log decision event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.DECISION,
            level=AuditLevel.INFO,
            operation=f"DECISION_{node}",
            details={
                'node': node,
                'decision': decision,
                'reason': reason,
                'next_node': next_node
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_action(self, action: str, description: str, details: Optional[Dict] = None,
                   transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log action event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.ACTION,
            level=AuditLevel.INFO,
            operation=action,
            details={
                'description': description,
                'details': details or {}
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_csv_operation(self, operation: str, file_path: str, records_affected: int,
                          success: bool, error: Optional[str] = None, details: Optional[Dict] = None,
                          transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log CSV operation event."""
        level = AuditLevel.ERROR if not success else AuditLevel.INFO

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.CSV_OPERATION,
            level=level,
            operation=operation,
            details={
                'file_path': file_path,
                'records_affected': records_affected,
                'success': success,
                'error': error,
                'details': details or {}
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_debit_authority(self, request_id: str, request_type: str, approved: bool,
                            creditor_agent_bic: str, amount: float, currency: str,
                            transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log debit authority event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.DEBIT_AUTHORITY,
            level=AuditLevel.INFO,
            operation="DEBIT_AUTHORITY",
            details={
                'request_id': request_id,
                'request_type': request_type,
                'approved': approved,
                'creditor_agent_bic': creditor_agent_bic,
                'amount': amount,
                'currency': currency
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_reconciliation(self, reconciliation_type: str, found: bool, match_type: str,
                           reference: str, uetr: str, amount: float, currency: str,
                           details: Optional[Dict] = None, transaction_id: Optional[str] = None,
                           correlation_id: Optional[str] = None):
        """Log reconciliation event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.RECONCILIATION,
            level=AuditLevel.INFO,
            operation=f"RECONCILIATION_{reconciliation_type}",
            details={
                'reconciliation_type': reconciliation_type,
                'found': found,
                'match_type': match_type,
                'reference': reference,
                'uetr': uetr,
                'amount': amount,
                'currency': currency,
                'details': details or {}
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_error(self, operation: str, error_message: str, error_details: Optional[Dict] = None,
                  transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log error event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.ERROR,
            level=AuditLevel.ERROR,
            operation=operation,
            details={
                'error_message': error_message,
                'error_details': error_details or {}
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def log_system_event(self, operation: str, description: str, details: Optional[Dict] = None,
                         transaction_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log system event."""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=AuditEventType.SYSTEM,
            level=AuditLevel.INFO,
            operation=operation,
            details={
                'description': description,
                'details': details or {}
            },
            session_id=self.session_id,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self._log_event(event)

    def _log_event(self, event: AuditEvent):
        """Internal method to log event."""
        self.events.append(event)
        self._write_to_csv(event)

    def _write_to_csv(self, event: AuditEvent):
        """Write event to CSV file."""
        try:
            # Check if file exists to determine if we need headers
            file_exists = False
            try:
                with open(self.audit_file, 'r'):
                    file_exists = True
            except FileNotFoundError:
                pass

            with open(self.audit_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'Event ID', 'Timestamp', 'Event Type', 'Level', 'Operation',
                    'Details', 'User', 'Session ID', 'Transaction ID', 'Correlation ID'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                writer.writerow({
                    'Event ID': event.event_id,
                    'Timestamp': event.timestamp,
                    'Event Type': event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type),
                    'Level': event.level.value if hasattr(event.level, 'value') else str(event.level),
                    'Operation': event.operation,
                    'Details': json.dumps(event.details, default=str),
                    'User': event.user,
                    'Session ID': event.session_id,
                    'Transaction ID': event.transaction_id,
                    'Correlation ID': event.correlation_id
                })
        except Exception as e:
            print(f"Error writing to audit log: {e}")

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.events)+1:03d}"

    def get_events_by_transaction(self, transaction_id: str) -> List[AuditEvent]:
        """Get all events for a specific transaction."""
        return [event for event in self.events if event.transaction_id == transaction_id]

    def get_events_by_correlation(self, correlation_id: str) -> List[AuditEvent]:
        """Get all events for a specific correlation ID."""
        return [event for event in self.events if event.correlation_id == correlation_id]

    def get_events_by_session(self, session_id: Optional[str] = None) -> List[AuditEvent]:
        """Get all events for a specific session."""
        target_session = session_id or self.session_id
        return [event for event in self.events if event.session_id == target_session]

    def get_events_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]

    def get_events_by_level(self, level: AuditLevel) -> List[AuditEvent]:
        """Get all events of a specific level."""
        return [event for event in self.events if event.level == level]

    def generate_audit_report(self, transaction_id: Optional[str] = None,
                              correlation_id: Optional[str] = None) -> Dict:
        """Generate comprehensive audit report."""
        if transaction_id:
            events = self.get_events_by_transaction(transaction_id)
        elif correlation_id:
            events = self.get_events_by_correlation(correlation_id)
        else:
            events = self.get_events_by_session()

        # Group events by type
        events_by_type = {}
        for event in events:
            event_type = event.event_type.value
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(asdict(event))

        # Calculate statistics
        total_events = len(events)
        error_events = len(self.get_events_by_level(AuditLevel.ERROR))
        warning_events = len(self.get_events_by_level(AuditLevel.WARNING))

        # Get decision path
        decision_events = [
            event for event in events if event.event_type == AuditEventType.DECISION]
        decision_path = [{'node': event.details.get('node'), 'decision': event.details.get('decision'),
                         'reason': event.details.get('reason')} for event in decision_events]

        # Get action summary
        action_events = [
            event for event in events if event.event_type == AuditEventType.ACTION]
        actions_taken = [{'action': event.operation, 'description': event.details.get('description')}
                         for event in action_events]

        return {
            'report_id': f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'session_id': self.session_id,
            'transaction_id': transaction_id,
            'correlation_id': correlation_id,
            'summary': {
                'total_events': total_events,
                'error_events': error_events,
                'warning_events': warning_events,
                'success_rate': ((total_events - error_events) / total_events * 100) if total_events > 0 else 0
            },
            'decision_path': decision_path,
            'actions_taken': actions_taken,
            'events_by_type': events_by_type,
            'all_events': [asdict(event) for event in events]
        }

    def export_audit_log(self, filename: Optional[str] = None) -> str:
        """Export audit log to JSON file."""
        if not filename:
            filename = f"{self.data_dir}/audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'total_events': len(self.events),
            'events': [asdict(event) for event in self.events]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2,
                      ensure_ascii=False, default=str)

        return filename

    def clear_session_events(self):
        """Clear events for current session."""
        self.events = []
        self.session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"


# Global audit logger instance
audit_logger = AuditLogger()
