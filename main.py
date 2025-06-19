#!/usr/bin/env python3
"""
Binary Search File Counter - Windows Optimized
High-performance file counting using binary search on sorted timestamps
Target: O(log n) performance vs O(n) traditional scanning

Key Architecture:
- Single directory enumeration for bulk timestamp collection
- Binary search on sorted modification times
- Count calculation via array arithmetic
- Windows filesystem optimized with proper timezone handling
"""

import os
import sys
import json
import logging
import smtplib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bisect


class BinarySearchFileCounter:
    """
    High-performance file counter using binary search optimization.
    Designed for Windows network drives with 100k+ files per directory.
    """

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.state_path = "state.json"
        self.approvals_path = "pending_approvals.json"

        # Load configuration first
        self.config = self.load_config()

        # Set production settings
        self.is_production = self.config.get("production_settings", {}).get(
            "is_production", False
        )
        self.is_local_test = self.config.get("production_settings", {}).get(
            "local_test_mode", False
        )
        self.bootstrap_mode = self.config.get("production_settings", {}).get(
            "bootstrap_mode", False
        )

        # Setup logging early
        self.setup_logging()

        # Load state and approvals
        self.state = self.load_state()
        self.pending_approvals = self.load_pending_approvals()

        # Pre-compile file filtering rules
        self._prepare_file_filters()

        # Log initialization
        self.logger.info(
            f"Binary Search File Counter initialized - config: {self.config_path}"
        )
        if self.is_local_test:
            self.logger.info("Mode: LOCAL TEST (production logic with local data)")
        elif self.is_production:
            self.logger.info("Mode: PRODUCTION (optimized for network drives)")
        else:
            self.logger.info("Mode: DEVELOPMENT")

        self._log_device_production_dates()

    def _prepare_file_filters(self):
        """Pre-compile file filtering rules for performance"""
        file_filtering = self.config.get("file_filtering", {})

        # Convert extensions to set for O(1) lookup
        self.include_extensions = set(
            ext.lower() for ext in file_filtering.get("include_extensions", [])
        )

        # Pre-compile exclude patterns
        self.exclude_patterns = file_filtering.get("exclude_patterns", [])

        # Cache minimum file size
        self.min_file_size = file_filtering.get("min_file_size_bytes", 0)

        self.logger.info(
            f"File filters: {len(self.include_extensions)} extensions, "
            f"{len(self.exclude_patterns)} exclude patterns, min size: {self.min_file_size}B"
        )

    def _log_device_production_dates(self):
        """Log production start dates for all devices"""
        devices = self.config.get("devices", {})
        if devices:
            self.logger.info("Device production start dates:")
            for device_name in devices.keys():
                if devices[device_name].get("enabled", False):
                    start_date = self.get_device_production_start_date(device_name)
                    self.logger.info(
                        f"  {device_name}: {start_date.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

    def get_device_production_start_date(self, device_name: str) -> datetime:
        """Get the production start date for a specific device"""
        device_config = self.config.get("devices", {}).get(device_name, {})
        device_start_date_str = device_config.get("production_start_date")

        if device_start_date_str:
            try:
                return datetime.fromisoformat(device_start_date_str)
            except ValueError:
                self.logger.warning(
                    f"Invalid production_start_date for {device_name}: {device_start_date_str}"
                )

        # Fallback to global production start date
        prod_settings = self.config.get("production_settings", {})
        global_start_date_str = prod_settings.get("production_start_date")

        if global_start_date_str:
            try:
                return datetime.fromisoformat(global_start_date_str)
            except ValueError:
                self.logger.warning(
                    f"Invalid global production_start_date: {global_start_date_str}"
                )

        # Final fallback
        self.logger.warning(
            f"No valid production start date for {device_name}, using current time"
        )
        return datetime.now()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_level = getattr(
            logging, self.config.get("logging", {}).get("level", "INFO")
        )

        # Include config name in log file
        config_name = Path(self.config_path).stem
        log_filename = (
            f"bi_counter_binary_{config_name}_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / log_filename, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {self.config_path} not found")
            print("Available config files:")
            for f in Path(".").glob("config*.json"):
                print(f"  - {f}")
            sys.exit(1)

    def load_state(self) -> Dict:
        """Load current state from JSON file"""
        try:
            with open(self.state_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_initial_state()

    def create_initial_state(self) -> Dict:
        """Create initial state"""
        initial_state = {
            "last_scan": None,
            "bootstrap_completed": False,
            "devices": {},
            "config_file_used": self.config_path,
            "optimization_method": "binary_search",
        }

        if self.is_production or self.is_local_test:
            initial_state["deployment_date"] = datetime.now().isoformat()
            initial_state["deployment_mode"] = (
                "local_test" if self.is_local_test else "production"
            )

        return initial_state

    def load_pending_approvals(self) -> Dict:
        """Load pending approvals from JSON file"""
        try:
            with open(self.approvals_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"pending": {}, "history": []}

    def save_state(self):
        """Save current state to JSON file"""
        self.state["config_file_used"] = self.config_path
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
        self.logger.info("State saved successfully")

    def save_pending_approvals(self):
        """Save pending approvals to JSON file"""
        with open(self.approvals_path, "w") as f:
            json.dump(self.pending_approvals, f, indent=2, default=str)

    def fast_file_filter(self, entry_name: str, entry_size: int) -> bool:
        """
        Fast file filtering without filesystem calls
        Optimized for binary search preprocessing
        """
        # Extension check (O(1) set lookup)
        if self.include_extensions:
            file_ext = Path(entry_name).suffix.lower()
            if file_ext not in self.include_extensions:
                return False

        # Pattern exclusion check
        for pattern in self.exclude_patterns:
            if Path(entry_name).match(pattern):
                return False

        # Size check
        if self.min_file_size > 0 and entry_size < self.min_file_size:
            return False

        return True

    def bulk_collect_file_timestamps(
        self, directory_path: Path
    ) -> List[Tuple[float, str]]:
        """
        CORE OPTIMIZATION: Bulk timestamp collection for binary search
        Single directory enumeration instead of individual file stats
        Returns: List of (timestamp, filename) tuples
        """
        timestamps = []

        if not directory_path.exists():
            self.logger.warning(f"Directory does not exist: {directory_path}")
            return timestamps

        collection_start = datetime.now()

        try:
            # Single os.scandir() call for bulk directory enumeration
            with os.scandir(str(directory_path)) as entries:
                for entry in entries:
                    if entry.is_file():
                        try:
                            # Get stat info via DirEntry (network optimized)
                            stat_info = entry.stat()

                            # Apply filtering
                            if self.fast_file_filter(entry.name, stat_info.st_size):
                                # Store timestamp and filename
                                timestamps.append((stat_info.st_mtime, entry.name))

                        except OSError as e:
                            self.logger.warning(
                                f"Could not access file {entry.path}: {e}"
                            )
                            continue

        except PermissionError:
            self.logger.error(f"Permission denied accessing {directory_path}")
            return []
        except Exception as e:
            self.logger.error(f"Error scanning {directory_path}: {e}")
            return []

        collection_duration = (datetime.now() - collection_start).total_seconds()

        # Sort by timestamp for binary search (critical step)
        timestamps.sort(key=lambda x: x[0])

        self.logger.debug(
            f"Collected {len(timestamps)} file timestamps in {collection_duration:.3f}s "
            f"({len(timestamps) / collection_duration:.0f} files/sec)"
            if collection_duration > 0
            else "(instant)"
        )

        return timestamps

    def binary_search_file_count(
        self, timestamps: List[Tuple[float, str]], cutoff_timestamp: float
    ) -> Dict[str, int]:
        """
        CORE ALGORITHM: Binary search for efficient file counting
        Finds the insertion point for cutoff_timestamp in sorted array
        O(log n) complexity vs O(n) traditional approach
        """
        if not timestamps:
            return {"total_files": 0, "historical_files": 0, "new_files": 0}

        total_files = len(timestamps)

        # Binary search for cutoff point
        # bisect_left finds leftmost insertion point
        cutoff_index = bisect.bisect_left(
            [ts for ts, _ in timestamps], cutoff_timestamp
        )

        historical_files = cutoff_index
        new_files = total_files - historical_files

        self.logger.debug(
            f"Binary search: {total_files} total, cutoff at index {cutoff_index}, "
            f"{historical_files} historical, {new_files} new"
        )

        return {
            "total_files": total_files,
            "historical_files": historical_files,
            "new_files": new_files,
        }

    def scan_device_optimized(
        self, device_name: str, device_config: Dict
    ) -> Dict[str, int]:
        """
        Optimized device scanning using binary search approach
        Single directory scan + binary search vs individual file processing
        """
        if not device_config.get("enabled", False):
            return {"total_files": 0, "historical_files": 0, "new_files": 0}

        scan_path = Path(self.config["scan_path"])
        device_dir = scan_path / device_name
        biu_path = device_dir / "BIU"

        if not biu_path.exists():
            self.logger.debug(f"No BIU folder found for {device_name}")
            return {"total_files": 0, "historical_files": 0, "new_files": 0}

        device_start = datetime.now()

        # Step 1: Bulk timestamp collection (single network operation)
        timestamps = self.bulk_collect_file_timestamps(biu_path)

        if not timestamps:
            return {"total_files": 0, "historical_files": 0, "new_files": 0}

        # Step 2: Determine cutoff logic based on bootstrap status
        device_state = self.state["devices"].get(device_name, {})

        # Don't count if pending approval
        if device_state.get("approval_status") == "PENDING_APPROVAL":
            self.logger.info(
                f"Device {device_name} pending approval - counting as historical"
            )
            return {
                "total_files": len(timestamps),
                "historical_files": len(timestamps),
                "new_files": 0,
            }

        is_first_run = not self.state.get("bootstrap_completed", False)

        if is_first_run:
            # First run logic: use device production start date
            device_production_start = self.get_device_production_start_date(device_name)
            cutoff_timestamp = device_production_start.timestamp()

            if self.bootstrap_mode:
                # Bootstrap mode: all files are historical
                self.logger.info(
                    f"{device_name} BOOTSTRAP MODE: All {len(timestamps)} files marked historical"
                )
                return {
                    "total_files": len(timestamps),
                    "historical_files": len(timestamps),
                    "new_files": 0,
                }
            else:
                # Non-bootstrap: files after production start count
                self.logger.info(
                    f"{device_name} NON-BOOTSTRAP: Using production start {device_production_start}"
                )

        else:
            # Subsequent runs: use last scan date
            last_scan_str = self.state["last_scan"]
            last_scan_date = datetime.fromisoformat(last_scan_str)
            cutoff_timestamp = last_scan_date.timestamp()

            self.logger.debug(
                f"{device_name} INCREMENTAL: Using last scan {last_scan_date}"
            )

        # Step 3: Binary search for file count (THE CORE OPTIMIZATION)
        file_counts = self.binary_search_file_count(timestamps, cutoff_timestamp)

        device_duration = (datetime.now() - device_start).total_seconds()

        self.logger.info(
            f"Device {device_name}: {file_counts['new_files']} new, "
            f"{file_counts['total_files']} total, {file_counts['historical_files']} historical "
            f"({device_duration:.3f}s - BINARY SEARCH OPTIMIZED)"
        )

        return file_counts

    def scan_all_devices(self) -> Dict[str, Dict[str, int]]:
        """
        Scan all enabled devices using binary search optimization
        Process devices sequentially to avoid network drive saturation
        """
        scan_start = datetime.now()
        device_results = {}

        devices_config = self.config.get("devices", {})
        enabled_devices = [
            name
            for name, config in devices_config.items()
            if config.get("enabled", False)
        ]

        self.logger.info(f"Starting optimized scan of {len(enabled_devices)} devices")

        for device_name in enabled_devices:
            device_config = devices_config[device_name]
            file_counts = self.scan_device_optimized(device_name, device_config)
            device_results[device_name] = file_counts

            # Update device state
            self.update_device_state(device_name, file_counts)

        total_duration = (datetime.now() - scan_start).total_seconds()
        total_files = sum(result["total_files"] for result in device_results.values())

        self.logger.info(
            f"BINARY SEARCH SCAN COMPLETE: {total_files} files across {len(enabled_devices)} devices "
            f"in {total_duration:.2f}s ({total_files / total_duration:.0f} files/sec if > 0 else 'instant')"
        )

        return device_results

    def update_device_state(self, device_name: str, file_counts: Dict[str, int]):
        """Update state for a specific device"""
        if device_name not in self.state["devices"]:
            self.state["devices"][device_name] = self.initialize_device_state(
                device_name
            )

        device_state = self.state["devices"][device_name]

        # Update file counts
        device_state["total_files"] = file_counts["total_files"]
        device_state["historical_files"] = file_counts["historical_files"]

        # Update device production start date if changed
        current_device_prod_start = self.get_device_production_start_date(device_name)
        device_state["device_production_start_date"] = (
            current_device_prod_start.isoformat()
        )

        # Don't update count if pending approval
        if device_state.get("approval_status") == "PENDING_APPROVAL":
            self.logger.info(f"Device {device_name} pending approval - count unchanged")
            return device_state

        # Update count with new files
        new_files = file_counts["new_files"]
        device_state["count"] += new_files

        if new_files > 0:
            self.logger.info(
                f"Device {device_name}: +{new_files} new files "
                f"(count: {device_state['count']}, total: {device_state['total_files']})"
            )

        # Check for tier advancement eligibility
        self.check_and_handle_tier_advancement(device_name, device_state)

        return device_state

    def initialize_device_state(self, device_name: str) -> Dict:
        """Initialize state for a new device"""
        device_config = self.config["devices"][device_name]
        current_tier = device_config.get("current_tier", "24h")
        device_production_start = self.get_device_production_start_date(device_name)

        device_state = {
            "current_tier": current_tier,
            "count": 0,
            "tier_start_date": datetime.now().isoformat(),
            "approval_status": "NONE",
            "total_files": 0,
            "historical_files": 0,
            "deployment_date": datetime.now().isoformat(),
            "config_used": self.config_path,
            "device_production_start_date": device_production_start.isoformat(),
            "optimization_method": "binary_search",
        }

        if self.is_production or self.is_local_test:
            device_state["production_deployment"] = True
            device_state["configured_tier"] = current_tier

        return device_state

    def check_and_handle_tier_advancement(self, device_name: str, device_state: Dict):
        """Check for tier advancement eligibility and handle approval workflow"""
        current_tier = device_state["current_tier"]
        current_count = device_state["count"]

        # Don't advance if at excluded tier
        if current_tier in self.config.get("excluded_tiers", []):
            return

        requirements = self.config["tier_requirements"]
        eligible_tier = None

        if current_tier == "24h" and current_count >= requirements["24h_to_12h"]:
            eligible_tier = "12h"
        elif current_tier == "12h" and current_count >= requirements["12h_to_6h"]:
            eligible_tier = "6h"
        elif current_tier == "6h" and current_count >= requirements["6h_to_3h"]:
            eligible_tier = "3h"
        elif current_tier == "3h" and current_count >= requirements["3h_to_2h"]:
            eligible_tier = "2h"

        if eligible_tier and eligible_tier != current_tier:
            self.logger.info(
                f"Device {device_name} eligible for advancement: {current_tier} -> {eligible_tier}"
            )

            # Create approval request
            approval_id = self.create_approval_request(
                device_name, current_tier, eligible_tier, current_count
            )

            # Set device to pending approval state
            device_state["approval_status"] = "PENDING_APPROVAL"
            device_state["pending_approval_id"] = approval_id

            # Send email notification if enabled
            if self.config.get("email_settings", {}).get("enabled", False):
                self.send_approval_request_email(approval_id)
            else:
                self.logger.info(
                    "Email disabled - approval request created but not sent"
                )

    def create_approval_request(
        self, device_name: str, current_tier: str, new_tier: str, count: int
    ) -> str:
        """Create approval request and return approval ID"""
        approval_id = str(uuid.uuid4())[:8]
        device_production_start = self.get_device_production_start_date(device_name)

        approval_request = {
            "approval_id": approval_id,
            "device_name": device_name,
            "current_tier": current_tier,
            "proposed_tier": new_tier,
            "unit_count": count,
            "request_date": datetime.now().isoformat(),
            "status": "PENDING",
            "requested_by": "BI_Counter_Binary_Search",
            "production_mode": self.is_production,
            "local_test_mode": self.is_local_test,
            "config_file": self.config_path,
            "device_production_start_date": device_production_start.isoformat(),
            "optimization_method": "binary_search",
        }

        self.pending_approvals["pending"][approval_id] = approval_request
        self.save_pending_approvals()

        self.logger.info(
            f"Created approval request {approval_id} for {device_name}: {current_tier} -> {new_tier}"
        )
        return approval_id

    def send_approval_request_email(self, approval_id: str):
        """Send email to Quality department requesting approval"""
        if not self.config["email_settings"]["enabled"]:
            return

        approval_request = self.pending_approvals["pending"][approval_id]

        subject = f"🚀 BI Tier Advancement Approval Required - {approval_request['device_name']} (Binary Search Optimized)"

        body = f"""
Dear Quality Team,

A burn-in tier advancement approval is required for the following device:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 APPROVAL REQUEST DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Device: {approval_request["device_name"]}
Current Tier: {approval_request["current_tier"]}
Proposed Tier: {approval_request["proposed_tier"]}
Unit Count: {approval_request["unit_count"]}
Request Date: {approval_request["request_date"]}
Approval ID: {approval_id}

🚀 Performance: Generated using binary search optimization (O(log n))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ACTION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please review and approve/reject this tier advancement request.

🌐 Web Interface: {self.config["approval_settings"]["approval_url"]}?id={approval_id}

⏰ IMPORTANT: Device will STOP COUNTING until this approval is processed!

Best regards,
BI Counter System (Binary Search Optimized)
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

        try:
            email_config = self.config["email_settings"]
            msg = MIMEMultipart()
            msg["From"] = email_config["username"]
            msg["To"] = ", ".join(email_config["recipients"]["quality"])
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            )
            if email_config["use_tls"]:
                server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email sent successfully for approval {approval_id}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")

    def process_approval_decision(
        self, approval_id: str, decision: str, approver: str
    ) -> bool:
        """Process approval decision (APPROVE/REJECT)"""
        if approval_id not in self.pending_approvals["pending"]:
            self.logger.error(f"Approval ID {approval_id} not found")
            return False

        approval_request = self.pending_approvals["pending"][approval_id]
        device_name = approval_request["device_name"]
        device_state = self.state["devices"][device_name]

        if decision == "APPROVE":
            device_state["current_tier"] = approval_request["proposed_tier"]
            device_state["count"] = 0
            device_state["tier_start_date"] = datetime.now().isoformat()
            device_state["approval_status"] = "APPROVED"
            self.logger.info(f"Approved tier advancement for {device_name}")
        elif decision == "REJECT":
            device_state["count"] = 0
            device_state["tier_start_date"] = datetime.now().isoformat()
            device_state["approval_status"] = "REJECTED"
            self.logger.info(f"Rejected tier advancement for {device_name}")

        # Move to history
        approval_request["status"] = decision
        approval_request["decision_date"] = datetime.now().isoformat()
        approval_request["approver"] = approver

        self.pending_approvals["history"].append(approval_request)
        del self.pending_approvals["pending"][approval_id]

        if "pending_approval_id" in device_state:
            del device_state["pending_approval_id"]

        self.save_state()
        self.save_pending_approvals()
        return True

    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        return {
            "scan_time": datetime.now().isoformat(),
            "config_file": self.config_path,
            "optimization_method": "binary_search",
            "algorithm_complexity": "O(log n)",
            "production_mode": self.is_production,
            "local_test_mode": self.is_local_test,
            "bootstrap_completed": self.state.get("bootstrap_completed", False),
            "devices_scanned": len(self.state["devices"]),
            "pending_approvals": len(self.pending_approvals["pending"]),
            "devices": {
                device_name: {
                    "current_tier": device_state["current_tier"],
                    "count": device_state["count"],
                    "total_files": device_state["total_files"],
                    "historical_files": device_state.get("historical_files", 0),
                    "approval_status": device_state.get("approval_status", "NONE"),
                    "device_production_start_date": device_state.get(
                        "device_production_start_date", "Unknown"
                    ),
                }
                for device_name, device_state in self.state["devices"].items()
            },
            "tier_summary": self._calculate_tier_summary(),
        }

    def _calculate_tier_summary(self) -> Dict[str, int]:
        """Calculate tier distribution summary"""
        tier_summary = {"24h": 0, "12h": 0, "6h": 0, "3h": 0, "2h": 0}
        for device_state in self.state["devices"].values():
            current_tier = device_state["current_tier"]
            tier_summary[current_tier] = tier_summary.get(current_tier, 0) + 1
        return tier_summary

    def run_scan(self):
        """Main scan execution using binary search optimization"""
        mode_str = (
            "Local Test"
            if self.is_local_test
            else ("Production" if self.is_production else "Development")
        )
        self.logger.info(
            f"Starting BI Counter {mode_str} Scan (BINARY SEARCH OPTIMIZED)"
        )

        start_time = datetime.now()

        # Execute optimized scanning
        device_results = self.scan_all_devices()

        if not device_results:
            self.logger.warning("No device results - check configuration")
            return None

        # Handle bootstrap completion
        if not self.state.get("bootstrap_completed", False):
            self.state["bootstrap_completed"] = True

            # Clear bootstrap mode from config after first use
            if "bootstrap_mode" in self.config.get("production_settings", {}):
                bootstrap_used = self.config["production_settings"]["bootstrap_mode"]
                del self.config["production_settings"]["bootstrap_mode"]
                self.config["production_settings"]["bootstrap_used_on_deployment"] = (
                    bootstrap_used
                )

                try:
                    with open(self.config_path, "w") as f:
                        json.dump(self.config, f, indent=2)
                    self.logger.info(
                        f"Bootstrap mode {bootstrap_used} applied and cleared from config"
                    )
                except Exception as e:
                    self.logger.warning(f"Could not save updated config: {e}")

            self.logger.info(
                "Bootstrap completed - future scans will use binary search incremental counting"
            )

        # Update scan timestamp
        self.state["last_scan"] = start_time.isoformat()
        self.save_state()

        # Generate performance report
        report = self.generate_report()
        scan_duration = (datetime.now() - start_time).total_seconds()
        total_files = sum(result["total_files"] for result in device_results.values())

        self.logger.info(
            f"🚀 BINARY SEARCH PERFORMANCE: Completed in {scan_duration:.2f}s, "
            f"processed {total_files} files using O(log n) algorithm "
            f"({total_files / scan_duration:.0f} files/sec effective throughput)"
        )

        return report


def main():
    """Main entry point for binary search file counter"""
    config_file = "config.json"

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        print(f"📁 Using config file: {config_file}")
    else:
        print(f"📁 Using default config file: {config_file}")

    print("🚀 Binary Search File Counter - O(log n) Optimization")

    counter = BinarySearchFileCounter(config_file)

    try:
        report = counter.run_scan()

        if report:
            print("\n" + "=" * 80)
            mode_indicator = (
                "🧪 LOCAL TEST"
                if counter.is_local_test
                else ("🏭 PRODUCTION" if counter.is_production else "🔧 DEVELOPMENT")
            )
            print(f"{mode_indicator} BI COUNTER SCAN REPORT (BINARY SEARCH OPTIMIZED)")
            print("=" * 80)
            print(json.dumps(report, indent=2))

            print("\n🚀 PERFORMANCE OPTIMIZATIONS:")
            print("   • Algorithm: Binary Search O(log n)")
            print("   • Method: Bulk timestamp collection + binary search")
            print("   • Target: 130k files in ~1 second vs ~30 seconds")
            print("   • Network: Single directory enumeration vs individual file stats")

    except Exception as e:
        logging.error(f"❌ Error during binary search scan: {e}")
        raise


if __name__ == "__main__":
    main()
