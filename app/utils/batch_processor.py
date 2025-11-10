"""
Batch Processing Utilities for Multiple Case Processing
Handles parallel processing, progress tracking, and batch operations.
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import uuid


class BatchProcessor:
    """Handles batch processing of multiple cases with progress tracking."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.active_batches = {}  # Store active batch processing sessions
        self.batch_results = {}   # Store batch results

    def create_batch_session(self, case_ids: List[str], user_id: str = None) -> str:
        """Create a new batch processing session."""
        batch_id = str(uuid.uuid4())

        self.active_batches[batch_id] = {
            "batch_id": batch_id,
            "case_ids": case_ids,
            "total_cases": len(case_ids),
            "processed_cases": 0,
            "successful_cases": 0,
            "failed_cases": 0,
            "status": "initialized",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "progress": 0.0,
            "results": [],
            "errors": [],
            "user_id": user_id,
            "cancelled": False
        }

        return batch_id

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get current status of a batch processing session."""
        if batch_id not in self.active_batches:
            return {"error": "Batch not found"}

        batch = self.active_batches[batch_id]
        return {
            "batch_id": batch_id,
            "status": batch["status"],
            "progress": batch["progress"],
            "total_cases": batch["total_cases"],
            "processed_cases": batch["processed_cases"],
            "successful_cases": batch["successful_cases"],
            "failed_cases": batch["failed_cases"],
            "start_time": batch["start_time"],
            "end_time": batch["end_time"],
            "cancelled": batch["cancelled"]
        }

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel an active batch processing session."""
        if batch_id in self.active_batches:
            self.active_batches[batch_id]["cancelled"] = True
            self.active_batches[batch_id]["status"] = "cancelled"
            return True
        return False

    def process_batch_parallel(self, batch_id: str, process_function: Callable) -> Dict[str, Any]:
        """Process multiple cases in parallel with progress tracking."""
        if batch_id not in self.active_batches:
            return {"error": "Batch not found"}

        batch = self.active_batches[batch_id]
        batch["status"] = "processing"

        try:
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all cases for processing
                future_to_case = {
                    executor.submit(process_function, case_id): case_id
                    for case_id in batch["case_ids"]
                }

                # Process completed futures
                for future in as_completed(future_to_case):
                    if batch["cancelled"]:
                        break

                    case_id = future_to_case[future]
                    try:
                        result = future.result()
                        batch["successful_cases"] += 1

                        # Ensure result is JSON serializable
                        serializable_result = {
                            "case_id": result.get("case_id", case_id),
                            "run_id": result.get("run_id"),
                            "status": result.get("status", "completed"),
                            "success": True,
                            "timestamp": datetime.now().isoformat()
                        }

                        batch["results"].append(serializable_result)
                    except Exception as e:
                        batch["failed_cases"] += 1
                        error_info = {
                            "case_id": case_id,
                            "status": "failed",
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                        batch["errors"].append(error_info)
                        batch["results"].append(error_info)

                    # Update progress
                    batch["processed_cases"] += 1
                    batch["progress"] = (
                        batch["processed_cases"] / batch["total_cases"]) * 100

                # Finalize batch
                batch["status"] = "cancelled" if batch["cancelled"] else "completed"
                batch["end_time"] = datetime.now().isoformat()

                # Store results for later retrieval
                self.batch_results[batch_id] = batch.copy()

                return {
                    "batch_id": batch_id,
                    "status": batch["status"],
                    "total_cases": batch["total_cases"],
                    "successful_cases": batch["successful_cases"],
                    "failed_cases": batch["failed_cases"],
                    "results": batch["results"]
                }

        except Exception as e:
            batch["status"] = "error"
            batch["end_time"] = datetime.now().isoformat()
            return {"error": f"Batch processing failed: {str(e)}"}

    def get_batch_results(self, batch_id: str) -> Dict[str, Any]:
        """Get detailed results of a completed batch."""
        if batch_id in self.batch_results:
            return self.batch_results[batch_id]
        elif batch_id in self.active_batches:
            return self.active_batches[batch_id]
        else:
            return {"error": "Batch not found"}


# Global batch processor instance
batch_processor = BatchProcessor(max_workers=4)
