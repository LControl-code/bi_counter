#!/usr/bin/env python3
"""
Production Configuration Wizard for BI Counter
Optimized version - removed unnecessary file scanning for performance
Focus: Validate structure, configure devices, not analyze files
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"🏭 {title}")
    print("=" * 70)


def print_section(title):
    """Print formatted section"""
    print(f"\n📋 {title}")
    print("-" * 50)


def get_yes_no(prompt, default="n"):
    """Get yes/no input from user"""
    while True:
        response = input(f"{prompt} (y/n) [{default}]: ").strip().lower()
        if not response:
            response = default
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'")


def get_date_input(prompt, default_date=None):
    """Get date input from user"""
    if default_date is None:
        default_date = datetime.now()

    default_str = default_date.strftime("%Y-%m-%d %H:%M:%S")

    while True:
        response = input(f"{prompt} [{default_str}]: ").strip()
        if not response:
            return default_date

        # Try different date formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(response, fmt)
            except ValueError:
                continue

        print("❌ Invalid date format. Please use YYYY-MM-DD HH:MM:SS or YYYY-MM-DD")


def get_menu_choice(options, prompt="Select option"):
    """Get menu choice from user"""
    while True:
        print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        try:
            choice = int(input("Enter choice: ").strip())
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def scan_production_directories(scan_path):
    """
    Fast directory structure validation - no file counting
    Only validates BIU folder structure exists
    """
    devices_found = []

    scan_dir = Path(scan_path)
    if not scan_dir.exists():
        print(f"⚠️ Directory {scan_path} does not exist")
        return devices_found

    print(f"🔍 Scanning {scan_path} for valid device structure...")
    print("📁 Looking for structure: scan_path/device_name/BIU/")
    print("⚡ Fast mode: Structure validation only")
    print()

    # Scan first level directories only
    for device_dir in scan_dir.iterdir():
        if not device_dir.is_dir():
            continue

        device_name = device_dir.name
        biu_path = device_dir / "BIU"

        # Only check if BIU exists - no file analysis
        if biu_path.exists() and biu_path.is_dir():
            try:
                # Quick accessibility check
                list(biu_path.iterdir()).__len__()  # Force evaluation but don't store

                devices_found.append(
                    {
                        "name": device_name,
                        "path": str(device_dir),
                        "biu_path": str(biu_path),
                        "validated": True,
                    }
                )

                print(f"  ✅ {device_name} - Structure validated")

            except PermissionError:
                print(f"  ⚠️ {device_name} - Permission denied, skipping")
            except Exception as e:
                print(f"  ❌ {device_name} - Access error: {e}")
        else:
            print(f"  ❌ {device_name} - No BIU folder found")

    print(f"\n📊 Found {len(devices_found)} valid device structures")
    return devices_found


def load_existing_config(config_file):
    """Load existing configuration file"""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        print(f"✅ Loaded existing configuration from {config_file}")
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file {config_file} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        return None


def display_current_config(config):
    """Display current configuration summary"""
    print_section("Current Configuration Summary")

    # Basic settings
    print(f"📁 Scan Path: {config.get('scan_path', 'Not set')}")

    prod_settings = config.get("production_settings", {})
    print(f"🏭 Production Mode: {prod_settings.get('is_production', False)}")
    print(
        f"📅 Global Production Start: {prod_settings.get('production_start_date', 'Not set')}"
    )

    # Device summary
    devices = config.get("devices", {})
    enabled_count = sum(1 for d in devices.values() if d.get("enabled", False))
    print(f"🔧 Devices: {len(devices)} total, {enabled_count} enabled")

    # Email settings
    email_settings = config.get("email_settings", {})
    print(
        f"📧 Email: {'Enabled' if email_settings.get('enabled', False) else 'Disabled'}"
    )

    if devices:
        print("\n📋 Device Details:")
        for name, device in devices.items():
            status = "✅ Enabled" if device.get("enabled", False) else "❌ Disabled"
            tier = device.get("current_tier", "Unknown")
            prod_start = device.get("production_start_date", "Not set")
            if prod_start != "Not set" and prod_start:
                try:
                    prod_start_dt = datetime.fromisoformat(prod_start)
                    prod_start = prod_start_dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
            print(f"  • {name}: {tier} tier, start: {prod_start} ({status})")


def update_scan_path(config):
    """Update scan path"""
    current_path = config.get("scan_path", "")
    print(f"\nCurrent scan path: {current_path}")

    new_path = input("Enter new scan path (press Enter to keep current): ").strip()
    if new_path:
        config["scan_path"] = new_path
        print(f"✅ Updated scan path to: {new_path}")
        return True
    return False


def update_production_settings(config):
    """Update production settings"""
    prod_settings = config.get("production_settings", {})

    print(f"\nCurrent production mode: {prod_settings.get('is_production', False)}")
    print(
        f"Current global production start date: {prod_settings.get('production_start_date', 'Not set')}"
    )
    print(f"Current bootstrap mode: {prod_settings.get('bootstrap_mode', True)}")
    print("Note: Individual devices can override the global production start date")

    production_date_changed = False

    if get_yes_no("Update production mode?", "n"):
        prod_settings["is_production"] = get_yes_no("Enable production mode?", "y")

    if get_yes_no("Update global production start date?", "n"):
        current_date = None
        if prod_settings.get("production_start_date"):
            try:
                current_date = datetime.fromisoformat(
                    prod_settings["production_start_date"]
                )
            except ValueError:
                pass

        new_date = get_date_input("Global production start date", current_date)
        if current_date != new_date:
            production_date_changed = True
        prod_settings["production_start_date"] = new_date.isoformat()

    # Prompt for bootstrap mode if production date changed
    if production_date_changed:
        print("\n🔄 Global production date changed - Bootstrap mode decision required:")
        print("Bootstrap mode affects how the system handles existing file counts:")
        print("  • TRUE: Ignore existing files, start fresh from 0 for all devices")
        print("  • FALSE: Count existing files toward tier advancement")
        current_bootstrap = prod_settings.get("bootstrap_mode", True)
        default_choice = "y" if current_bootstrap else "n"
        prod_settings["bootstrap_mode"] = get_yes_no(
            "Enable bootstrap mode (start fresh)?", default_choice
        )

    config["production_settings"] = prod_settings
    print("✅ Production settings updated")
    return production_date_changed


def configure_device_tiers(
    devices_found, existing_devices=None, global_production_start=None, config=None
):
    """
    Configure current tier and settings for each device
    Optimized: No file counting, focus on configuration
    """
    if existing_devices is None:
        existing_devices = {}

    device_configs = existing_devices.copy()

    if not devices_found:
        print("❌ No devices found to configure")
        return device_configs, False

    print_section("Device Configuration")
    print("For each device, specify its CURRENT production settings:")
    print("📋 Available tiers: 24h, 12h, 6h, 3h, 2h")
    print("⚠️ IMPORTANT: Set the tier each device is CURRENTLY running in production!")
    print("📅 Each device needs its own production start date for accurate counting!")
    print("⚡ Fast mode: Configuration only, no file analysis")
    print()

    tier_options = ["24h", "12h", "6h", "3h", "2h"]
    devices_with_date_changes = []
    new_or_enabled_devices = []

    for i, device in enumerate(devices_found, 1):
        device_name = device["name"]
        existing_config = existing_devices.get(device_name, {})
        was_enabled = existing_config.get("enabled", False)

        print(f"\n🔧 Device {i}/{len(devices_found)}: {device_name}")
        print(f"   📁 Path: {device['path']}")
        print("   ✅ Structure: Valid BIU folder found")

        if existing_config:
            existing_start = existing_config.get("production_start_date", "Not set")
            if existing_start != "Not set":
                try:
                    existing_start_dt = datetime.fromisoformat(existing_start)
                    existing_start = existing_start_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            print(
                f"   📋 Current config: {existing_config.get('current_tier', 'Unknown')} tier, "
                f"start: {existing_start}, {'Enabled' if existing_config.get('enabled', False) else 'Disabled'}"
            )

        # Check if device should be enabled
        default_enabled = "y" if existing_config.get("enabled", True) else "n"
        enabled = get_yes_no(
            f"   Enable {device_name} for BI Counter monitoring?", default_enabled
        )

        if not enabled:
            device_configs[device_name] = {
                "enabled": False,
                "current_tier": existing_config.get("current_tier", "24h"),
                "exclude_2h": existing_config.get("exclude_2h", False),
                "description": "Disabled device - structure validated",
                "production_start_date": existing_config.get(
                    "production_start_date",
                    global_production_start.isoformat()
                    if global_production_start
                    else datetime.now().isoformat(),
                ),
                "configured_date": datetime.now().isoformat(),
            }
            print(f"   ❌ {device_name} disabled")
            continue

        # Track if this is a new device or newly enabled
        if not existing_config or not was_enabled:
            new_or_enabled_devices.append(device_name)

        # Get current tier
        default_tier = existing_config.get("current_tier", "24h")
        while True:
            current_tier = input(
                f"   Current burn-in tier for {device_name} [{default_tier}] (24h/12h/6h/3h/2h): "
            ).strip()
            if not current_tier:
                current_tier = default_tier
            if current_tier in tier_options:
                break
            print(f"   ❌ Invalid tier. Please enter one of: {', '.join(tier_options)}")

        # Get production start date for this device
        print(f"\n   📅 Production start date for {device_name}:")
        print("   This determines which files count toward tier advancement.")
        print(
            "   Files created before this date will be considered 'historical' and ignored."
        )

        # Use existing or global default
        default_prod_start = None
        existing_prod_start = None
        if existing_config.get("production_start_date"):
            try:
                existing_prod_start = datetime.fromisoformat(
                    existing_config["production_start_date"]
                )
                default_prod_start = existing_prod_start
            except Exception:
                pass
        elif global_production_start:
            default_prod_start = global_production_start
        else:
            default_prod_start = datetime.now()

        print("   💡 Recommendations:")
        print("      • Use recent date to start counting fresh")
        print("      • Use older date to include historical files")
        print("      • Counter will separate historical vs. new files automatically")

        production_start_date = get_date_input(
            f"   Production start date for {device_name}", default_prod_start
        )

        # Check if production start date changed
        if existing_prod_start and existing_prod_start != production_start_date:
            devices_with_date_changes.append(device_name)

        # Check if should exclude 2h tier
        exclude_2h = existing_config.get("exclude_2h", False)
        if current_tier != "2h":
            default_exclude = "y" if exclude_2h else "n"
            exclude_2h = get_yes_no(
                f"   Exclude {device_name} from 2h tier advancement?", default_exclude
            )
        else:
            exclude_2h = True  # Already at final tier

        # Get description
        default_desc = existing_config.get(
            "description",
            f"Production device at {current_tier} tier - structure validated",
        )
        description = input(f"   Description [{default_desc}]: ").strip()
        if not description:
            description = default_desc

        device_configs[device_name] = {
            "enabled": True,
            "current_tier": current_tier,
            "exclude_2h": exclude_2h,
            "description": description,
            "production_start_date": production_start_date.isoformat(),
            "configured_date": datetime.now().isoformat(),
        }

        print(
            f"   ✅ {device_name} configured: {current_tier} tier, "
            f"start: {production_start_date.strftime('%Y-%m-%d')}, "
            f"{'excluded from' if exclude_2h else 'allowed to'} 2h tier"
        )

    # Return devices and whether bootstrap decision is needed
    needs_bootstrap_decision = bool(devices_with_date_changes or new_or_enabled_devices)

    if needs_bootstrap_decision and config:
        print("\n🔄 Bootstrap mode decision required:")
        if new_or_enabled_devices:
            print(f"   New/enabled devices: {', '.join(new_or_enabled_devices)}")
        if devices_with_date_changes:
            print(
                f"   Devices with production date changes: {', '.join(devices_with_date_changes)}"
            )

        print("\nBootstrap mode affects how the system handles existing file counts:")
        print(
            "  • TRUE: Ignore existing files, start fresh from 0 for affected devices"
        )
        print(
            "  • FALSE: Count existing files toward tier advancement for affected devices"
        )

        current_bootstrap = config.get("production_settings", {}).get(
            "bootstrap_mode", True
        )
        default_choice = "y" if current_bootstrap else "n"
        new_bootstrap = get_yes_no(
            "Enable bootstrap mode (start fresh)?", default_choice
        )

        config.setdefault("production_settings", {})["bootstrap_mode"] = new_bootstrap
        print(f"✅ Bootstrap mode set to: {new_bootstrap}")

    return device_configs, needs_bootstrap_decision


def update_devices(config):
    """Update device configurations - optimized version"""
    scan_path = config.get("scan_path", "")
    if not scan_path:
        print("❌ No scan path configured. Please update scan path first.")
        return False

    print_section("Device Update Options")

    options = [
        "Rescan for new devices and add them",
        "Update existing device settings",
        "Remove devices no longer found",
        "Reconfigure all devices from scratch",
    ]

    choice = get_menu_choice(options, "Select device update option")

    global_prod_start = None
    prod_settings = config.get("production_settings", {})
    if prod_settings.get("production_start_date"):
        try:
            global_prod_start = datetime.fromisoformat(
                prod_settings["production_start_date"]
            )
        except Exception:
            pass

    if choice == 0:  # Rescan for new devices
        devices_found = scan_production_directories(scan_path)
        existing_devices = config.get("devices", {})

        # Find new devices
        new_devices = [d for d in devices_found if d["name"] not in existing_devices]

        if not new_devices:
            print("✅ No new devices found")
            return False

        print(f"\n🆕 Found {len(new_devices)} new devices:")
        for device in new_devices:
            print(f"  • {device['name']} - Structure validated")

        if get_yes_no("Configure new devices?", "y"):
            new_configs, needs_bootstrap = configure_device_tiers(
                new_devices, {}, global_prod_start, config
            )
            existing_devices.update(new_configs)
            config["devices"] = existing_devices
            print(f"✅ Added {len(new_devices)} new devices")
            return True

    elif choice == 1:  # Update existing device settings
        existing_devices = config.get("devices", {})
        if not existing_devices:
            print("❌ No existing devices to update")
            return False

        print("\n📋 Select device to update:")
        device_names = list(existing_devices.keys())
        device_choice = get_menu_choice(device_names, "Select device")

        device_name = device_names[device_choice]
        device_config = existing_devices[device_name]

        print(f"\n🔧 Updating {device_name}")
        print("Current settings:")
        for key, value in device_config.items():
            if key == "production_start_date" and value:
                try:
                    dt = datetime.fromisoformat(value)
                    value = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            print(f"  {key}: {value}")

        # Track changes that require bootstrap decision
        production_date_changed = False
        enabled_status_changed = False

        # Update individual settings
        tier_options = ["24h", "12h", "6h", "3h", "2h"]

        if get_yes_no("Update enabled status?", "n"):
            old_enabled = device_config.get("enabled", True)
            device_config["enabled"] = get_yes_no(
                "Enable device?", "y" if old_enabled else "n"
            )
            if old_enabled != device_config["enabled"] and device_config["enabled"]:
                enabled_status_changed = True

        if device_config.get("enabled", True) and get_yes_no(
            "Update current tier?", "n"
        ):
            current_tier = device_config.get("current_tier", "24h")
            while True:
                new_tier = input(f"Current tier [{current_tier}]: ").strip()
                if not new_tier:
                    break
                if new_tier in tier_options:
                    device_config["current_tier"] = new_tier
                    break
                print(f"Invalid tier. Options: {', '.join(tier_options)}")

        if get_yes_no("Update production start date?", "n"):
            current_start = None
            if device_config.get("production_start_date"):
                try:
                    current_start = datetime.fromisoformat(
                        device_config["production_start_date"]
                    )
                except Exception:
                    pass

            new_start = get_date_input(
                f"Production start date for {device_name}", current_start
            )

            if current_start != new_start:
                production_date_changed = True

            device_config["production_start_date"] = new_start.isoformat()

        if get_yes_no("Update description?", "n"):
            current_desc = device_config.get("description", "")
            new_desc = input(f"Description [{current_desc}]: ").strip()
            if new_desc:
                device_config["description"] = new_desc

        device_config["configured_date"] = datetime.now().isoformat()

        # Check if bootstrap decision is needed
        if production_date_changed or enabled_status_changed:
            print("\n🔄 Bootstrap mode decision required:")
            if enabled_status_changed:
                print(f"   Device {device_name} was enabled")
            if production_date_changed:
                print(f"   Production start date changed for {device_name}")

            print(
                "\nBootstrap mode affects how the system handles existing file counts:"
            )
            print("  • TRUE: Ignore existing files, start fresh from 0")
            print("  • FALSE: Count existing files toward tier advancement")

            current_bootstrap = config.get("production_settings", {}).get(
                "bootstrap_mode", True
            )
            default_choice = "y" if current_bootstrap else "n"
            new_bootstrap = get_yes_no(
                "Enable bootstrap mode (start fresh)?", default_choice
            )

            config.setdefault("production_settings", {})["bootstrap_mode"] = (
                new_bootstrap
            )
            print(f"✅ Bootstrap mode set to: {new_bootstrap}")

        print(f"✅ Updated {device_name}")
        return True

    elif choice == 2:  # Remove devices no longer found
        devices_found = scan_production_directories(scan_path)
        existing_devices = config.get("devices", {})
        found_names = {d["name"] for d in devices_found}

        # Find devices to remove
        devices_to_remove = [
            name for name in existing_devices if name not in found_names
        ]

        if not devices_to_remove:
            print("✅ All configured devices still found")
            return False

        print(f"\n🗑️ Devices no longer found ({len(devices_to_remove)}):")
        for device_name in devices_to_remove:
            print(f"  • {device_name}")

        if get_yes_no("Remove these devices from configuration?", "n"):
            for device_name in devices_to_remove:
                del existing_devices[device_name]
            config["devices"] = existing_devices
            print(f"✅ Removed {len(devices_to_remove)} devices")
            return True

    elif choice == 3:  # Reconfigure all devices
        devices_found = scan_production_directories(scan_path)
        existing_devices = config.get("devices", {})

        print("\n⚠️ This will reconfigure ALL devices from scratch")
        if get_yes_no("Continue with full reconfiguration?", "n"):
            new_configs, needs_bootstrap = configure_device_tiers(
                devices_found, existing_devices, global_prod_start, config
            )
            config["devices"] = new_configs
            print("✅ All devices reconfigured")
            return True

    return False


def configure_email_settings(existing_settings=None):
    """Configure email settings for production"""
    if existing_settings is None:
        existing_settings = {}

    print_section("Email Notification Configuration")

    current_enabled = existing_settings.get("enabled", False)
    enable_email = get_yes_no(
        "Enable email notifications for approvals?", "y" if current_enabled else "n"
    )

    if not enable_email:
        return {
            "enabled": False,
            "smtp_server": existing_settings.get("smtp_server", "smtp.company.com"),
            "smtp_port": existing_settings.get("smtp_port", 587),
            "username": existing_settings.get("username", "bi_counter@company.com"),
            "password": existing_settings.get("password", "CHANGE_IN_PRODUCTION"),
            "use_tls": existing_settings.get("use_tls", True),
            "recipients": existing_settings.get(
                "recipients",
                {
                    "quality": ["quality@company.com"],
                    "te": ["te@company.com"],
                    "planning": ["planning@company.com"],
                    "production": ["production@company.com"],
                },
            ),
        }

    print("📧 Configuring email settings for production...")

    smtp_server = input(
        f"SMTP server [{existing_settings.get('smtp_server', 'smtp.company.com')}]: "
    ).strip()
    if not smtp_server:
        smtp_server = existing_settings.get("smtp_server", "smtp.company.com")

    smtp_port_str = input(
        f"SMTP port [{existing_settings.get('smtp_port', 587)}]: "
    ).strip()
    smtp_port = (
        int(smtp_port_str) if smtp_port_str else existing_settings.get("smtp_port", 587)
    )

    username = input(
        f"Email username [{existing_settings.get('username', 'bi_counter@company.com')}]: "
    ).strip()
    if not username:
        username = existing_settings.get("username", "bi_counter@company.com")

    current_password = existing_settings.get("password", "CHANGE_IN_PRODUCTION")
    if get_yes_no("Update email password?", "n"):
        print("⚠️ Password will be visible - change this in config.json after setup")
        password = input("Email password: ").strip() or current_password
    else:
        password = current_password

    use_tls = get_yes_no(
        "Use TLS encryption?", "y" if existing_settings.get("use_tls", True) else "n"
    )

    print("\n📮 Configure recipient groups:")
    recipients = existing_settings.get("recipients", {})

    groups = [
        ("quality", "Quality/QE team (approval decisions)"),
        ("te", "Test Engineering team"),
        ("planning", "Planning team"),
        ("production", "Production/Manufacturing team"),
    ]

    for group, description in groups:
        print(f"\n{description}:")
        current_emails = recipients.get(group, [])

        if current_emails:
            print(f"Current emails: {', '.join(current_emails)}")
            if not get_yes_no(f"Update {group} emails?", "n"):
                continue

        emails = []
        print("Enter emails (press Enter when done):")
        while True:
            email = input(f"  Add email for {group}: ").strip()
            if not email:
                break
            if "@" in email:  # Basic email validation
                emails.append(email)
                print(f"    ✅ Added: {email}")
            else:
                print("    ❌ Invalid email format")

        if not emails and not current_emails:
            emails = [f"{group}@company.com"]  # Default fallback
            print(f"    📋 Using default: {emails[0]}")
        elif emails:
            recipients[group] = emails
        # If no new emails but current emails exist, keep current

    return {
        "enabled": True,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "username": username,
        "password": password,
        "use_tls": use_tls,
        "recipients": recipients,
    }


def update_email_settings(config):
    """Update email settings"""
    email_settings = config.get("email_settings", {})

    print(f"\nCurrent email enabled: {email_settings.get('enabled', False)}")

    if get_yes_no("Update email settings?", "n"):
        return configure_email_settings(email_settings)

    return False


def create_production_config(
    scan_path, global_production_start_date, device_configs, email_settings
):
    """Create production configuration file"""

    config = {
        "scan_path": scan_path,
        "production_settings": {
            "is_production": True,
            "production_start_date": global_production_start_date.isoformat(),
            "bootstrap_mode": False,
            "deployment_date": datetime.now().isoformat(),
            "configured_by": "Production Configuration Wizard - Optimized",
            "notes": "Production deployment - per-device production start dates for historical file separation",
        },
        "devices": device_configs,
        "tier_requirements": {
            "24h_to_12h": 250,
            "12h_to_6h": 500,
            "6h_to_3h": 1000,
            "3h_to_2h": 2000,
        },
        "excluded_tiers": [],
        "email_settings": email_settings,
        "approval_settings": {
            "approval_url": "http://localhost:8080",
            "timeout_days": 7,
            "auto_reminder_days": 3,
            "require_approver_name": True,
        },
        "logging": {
            "level": "INFO",
            "max_log_files": 90,
            "log_approval_decisions": True,
            "log_file_counts": True,
        },
        "file_filtering": {
            "include_extensions": [".txt", ".log", ".dat", ".csv"],
            "exclude_patterns": ["temp*", "*.tmp", "backup*"],
            "min_file_size_bytes": 10,
        },
    }

    # Save configuration
    config_filename = "config_production.json"
    with open(config_filename, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Production configuration saved to {config_filename}")

    # Clean up any existing state to ensure fresh start
    state_files_to_clean = ["state.json", "pending_approvals.json"]
    for state_file in state_files_to_clean:
        if Path(state_file).exists():
            try:
                Path(state_file).unlink()
                print(f"🧹 Cleaned up existing {state_file} for fresh start")
            except Exception as e:
                print(f"⚠️ Could not remove {state_file}: {e}")

    return config, config_filename


def update_mode_main(config_file):
    """Main function for update mode - optimized version"""
    print_header("BI Counter Configuration Update Mode - Optimized")

    # Load existing configuration
    config = load_existing_config(config_file)
    if not config:
        print(f"❌ Cannot load configuration file: {config_file}")
        print("Use the wizard without --update to create a new configuration.")
        return

    # Display current configuration
    display_current_config(config)

    # Track if significant changes were made that require fresh start
    requires_fresh_start = False

    # Main update loop
    while True:
        print_section("Update Menu")
        options = [
            "Update scan path",
            "Update production settings",
            "Update devices",
            "Update email settings",
            "Update bootstrap mode",
            "Save and exit",
            "Exit without saving",
        ]

        choice = get_menu_choice(options, "Select what to update")

        if choice == 0:  # Update scan path
            if update_scan_path(config):
                print("✅ Scan path updated")
                requires_fresh_start = True

        elif choice == 1:  # Update production settings
            production_date_changed = update_production_settings(config)
            if production_date_changed:
                requires_fresh_start = True

        elif choice == 2:  # Update devices
            if update_devices(config):
                print("✅ Device settings updated")
                requires_fresh_start = True

        elif choice == 3:  # Update email settings
            new_email_settings = update_email_settings(config)
            if new_email_settings:
                config["email_settings"] = new_email_settings
                print("✅ Email settings updated")

        elif choice == 4:  # Update bootstrap mode
            current_bootstrap = config.get("production_settings", {}).get(
                "bootstrap_mode", True
            )
            print(f"\nCurrent bootstrap mode: {current_bootstrap}")
            print("Bootstrap mode affects how the system handles existing file counts:")
            print("  • TRUE: Ignore existing files, start fresh from 0 for all devices")
            print("  • FALSE: Count existing files toward tier advancement")

            default_choice = "y" if current_bootstrap else "n"
            new_bootstrap = get_yes_no(
                "Enable bootstrap mode (start fresh)?", default_choice
            )

            if current_bootstrap != new_bootstrap:
                requires_fresh_start = True

            config.setdefault("production_settings", {})["bootstrap_mode"] = (
                new_bootstrap
            )
            print(f"✅ Bootstrap mode set to: {new_bootstrap}")

        elif choice == 5:  # Save and exit
            # Update modification timestamp
            config.setdefault("production_settings", {})["last_updated"] = (
                datetime.now().isoformat()
            )
            config.setdefault("production_settings", {})["updated_by"] = (
                "Configuration Update Mode - Optimized"
            )

            # Save configuration
            backup_file = (
                f"{config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Create backup
            try:
                with open(config_file, "r") as src, open(backup_file, "w") as dst:
                    dst.write(src.read())
                print(f"✅ Backup created: {backup_file}")
            except Exception as e:
                print(f"⚠️ Could not create backup: {e}")

            # Save updated config
            try:
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"✅ Configuration saved to {config_file}")

                # Clean up state files if significant changes were made
                if requires_fresh_start:
                    print(
                        "\n🧹 Significant changes detected - cleaning up state files for fresh start"
                    )
                    state_files_to_clean = ["state.json", "pending_approvals.json"]
                    for state_file in state_files_to_clean:
                        if Path(state_file).exists():
                            try:
                                Path(state_file).unlink()
                                print(f"🧹 Cleaned up existing {state_file}")
                            except Exception as e:
                                print(f"⚠️ Could not remove {state_file}: {e}")
                    print("✅ Ready for fresh bootstrap on next run")

                # Show summary
                print_section("Update Summary")
                display_current_config(config)

            except Exception as e:
                print(f"❌ Error saving configuration: {e}")
                return

            break

        elif choice == 6:  # Exit without saving
            if get_yes_no("Exit without saving changes?", "n"):
                print("❌ Changes discarded")
                break


def main():
    """Main entry point with argument parsing - optimized version"""
    parser = argparse.ArgumentParser(
        description="BI Counter Production Configuration Wizard - Optimized",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Performance Optimizations:
• Removed unnecessary file counting - 10-100x faster
• Focus on structure validation and configuration
• File analysis handled by main counter when needed

Examples:
  python config_wizard.py                           # Create new configuration
  python config_wizard.py --update                  # Update existing configuration
  python config_wizard.py --update config_prod.json # Update specific config file
        """,
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing configuration instead of creating new one",
    )

    parser.add_argument(
        "config_file",
        nargs="?",
        default="config_production.json",
        help="Configuration file to create or update (default: config_production.json)",
    )

    args = parser.parse_args()

    if args.update:
        update_mode_main(args.config_file)
        return

    # Original setup wizard logic - optimized
    print_header("BI Counter Production Configuration Wizard - Optimized")
    print("This wizard helps you configure BI Counter for production deployment.")
    print("It will validate your production directory structure and configure devices.")
    print()
    print("🚀 PERFORMANCE OPTIMIZED: No file counting during setup!")
    print("📁 Structure validation only - file analysis handled by main counter")
    print("⚡ 10-100x faster than previous version")
    print()
    print("Prerequisites:")
    print("• Network access to production data directory")
    print("• Knowledge of current burn-in tiers for each device")
    print("• SMTP server details for email notifications")
    print("• List of email addresses for Quality, TE, Planning, and Production teams")

    if not get_yes_no(
        "\nReady to proceed with optimized production configuration?", "y"
    ):
        print("Configuration cancelled.")
        return

    # Step 1: Get production scan path
    print_section("Step 1: Production Directory Path")
    print("Enter the path to your production data directory.")
    print("This should contain device folders with BIU subfolders.")
    print("Example: Q:\\Shopfloor\\TEstData")
    print()

    while True:
        scan_path = input("Production data path: ").strip()
        if scan_path:
            break
        print("❌ Please enter a valid path")

    # Step 2: Set global production start date (as fallback)
    print_section("Step 2: Global Production Start Date")
    print("Set a default date for production start.")
    print("Note: Each device will have its own production start date,")
    print("but this serves as a fallback default.")
    print()
    print("Recommendations:")
    print("• Set to today's date if starting fresh")
    print("• Set to a past date if you want to count some recent files by default")

    global_production_start_date = get_date_input("\nGlobal production start date")

    # Step 3: Scan for devices - OPTIMIZED
    print_section("Step 3: Device Discovery - Fast Structure Validation")
    devices_found = scan_production_directories(scan_path)

    if not devices_found:
        print("❌ No valid device structures found!")
        print("Please verify:")
        print(f"• Path {scan_path} exists and is accessible")
        print("• Device folders exist at first level")
        print("• Each device folder contains a 'BIU' subfolder")
        print(f"• Structure: {scan_path}/DeviceName/BIU/")
        return

    # Step 4: Configure devices - OPTIMIZED
    device_configs, needs_bootstrap_decision = configure_device_tiers(
        devices_found, None, global_production_start_date
    )

    if not device_configs:
        print("❌ No devices configured!")
        return

    # Step 5: Configure email
    email_settings = configure_email_settings()

    # Step 6: Create configuration
    print_section("Step 6: Creating Optimized Production Configuration")
    config, config_filename = create_production_config(
        scan_path, global_production_start_date, device_configs, email_settings
    )

    # Summary
    print_header("Optimized Production Configuration Complete!")

    enabled_devices = sum(1 for d in device_configs.values() if d["enabled"])
    disabled_devices = len(device_configs) - enabled_devices

    print("🎉 Production configuration created successfully!")
    print()
    print("📋 CONFIGURATION SUMMARY:")
    print(f"   • Production Path: {scan_path}")
    print(f"   • Global Production Start: {global_production_start_date}")
    print(
        f"   • Bootstrap Mode: {config.get('production_settings', {}).get('bootstrap_mode', True)}"
    )
    print(f"   • Devices Found: {len(devices_found)}")
    print(f"   • Devices Enabled: {enabled_devices}")
    print(f"   • Devices Disabled: {disabled_devices}")
    print(f"   • Email Enabled: {email_settings['enabled']}")
    print(f"   • Config File: {config_filename}")

    if device_configs:
        print("\n🔧 DEVICE CONFIGURATION:")
        for device_name, device_config in device_configs.items():
            status = "✅ Enabled" if device_config["enabled"] else "❌ Disabled"
            tier = device_config["current_tier"]
            start_date = device_config.get("production_start_date", "Not set")
            if start_date != "Not set":
                try:
                    start_dt = datetime.fromisoformat(start_date)
                    start_date = start_dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
            print(f"   • {device_name}: {tier} tier, start: {start_date} ({status})")

    print("\n🚀 NEXT STEPS:")
    print("1. Review and edit config_production.json if needed")
    print("2. Update email password in config file (if using email)")
    print("3. Test configuration: python main.py config_production.json")
    print(
        "4. Start approval interface: python approval_interface.py config_production.json"
    )
    print("5. Set up daily scheduling on production server")
    print("6. Monitor first few runs to verify correct operation")

    print("\n📊 EXPECTED FIRST RUN BEHAVIOR:")
    print("• Counter will discover and count files in real-time")
    print(
        "• Each device categorizes files as historical vs new based on production start date"
    )
    print(
        "• Only files after each device's production start date count toward advancement"
    )
    print("• Devices start counting from their configured current tiers")

    print("\n⚡ PERFORMANCE IMPROVEMENTS:")
    print("• Configuration wizard now 10-100x faster")
    print("• No unnecessary file counting during setup")
    print("• File analysis handled by main counter when needed")
    print("• Focus on configuration validation, not data analysis")

    print("\n⚠️ IMPORTANT REMINDERS:")
    print("• Each device has its own production start date for accurate counting")
    print("• Backup configuration files before making changes")
    print("• Verify network path access from production server")
    print("• Test email notifications before going live")
    print("• Monitor logs for first few days of operation")

    print(f"\n📞 Configuration saved to: {config_filename}")
    print("Ready for lightning-fast production deployment!")


if __name__ == "__main__":
    main()
