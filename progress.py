"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Now uses the Feature API instead of reading feature_list.json directly.
"""

import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path


API_BASE_URL = "http://localhost:8765"
WEBHOOK_URL = os.environ.get("PROGRESS_N8N_WEBHOOK_URL")
PROGRESS_CACHE_FILE = ".progress_cache"


def has_features(project_dir: Path) -> bool:
    """
    Check if the project has features in the database.

    This is used to determine if the initializer agent needs to run.
    We check the database directly (not via API) since the API server
    may not be running yet when this check is performed.

    Returns True if:
    - features.db exists AND has at least 1 feature, OR
    - feature_list.json exists (legacy format)

    Returns False if no features exist (initializer needs to run).
    """
    import sqlite3

    # Check legacy JSON file first
    json_file = project_dir / "feature_list.json"
    if json_file.exists():
        return True

    # Check SQLite database
    db_file = project_dir / "features.db"
    if not db_file.exists():
        return False

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM features")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        # Database exists but can't be read or has no features table
        return False


def _api_get(endpoint: str) -> dict:
    """
    Make a GET request to the Feature API.

    Args:
        endpoint: API endpoint (e.g., "/features/stats")

    Returns:
        Parsed JSON response

    Raises:
        Exception if request fails
    """
    url = f"{API_BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests via the Feature API.

    Args:
        project_dir: Directory containing the project (unused, kept for compatibility)

    Returns:
        (passing_count, total_count)
    """
    try:
        stats = _api_get("/features/stats")
        return stats["passing"], stats["total"]
    except Exception as e:
        # API not available - might be first run before server starts
        # Fall back to checking if database exists
        print(f"[API unavailable in count_passing_tests: {e}]")
        return 0, 0


def send_progress_webhook(passing: int, total: int, project_dir: Path) -> None:
    """Send webhook notification when progress increases."""
    if not WEBHOOK_URL:
        return  # Webhook not configured

    cache_file = project_dir / PROGRESS_CACHE_FILE
    previous = 0
    previous_passing_ids = set()

    # Read previous progress and passing feature IDs
    if cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text())
            previous = cache_data.get("count", 0)
            previous_passing_ids = set(cache_data.get("passing_ids", []))
        except Exception:
            previous = 0

    # Only notify if progress increased
    if passing > previous:
        # Find which features are now passing via API
        completed_tests = []
        current_passing_ids = []

        # Detect transition from old cache format (had count but no passing_ids)
        # In this case, we can't reliably identify which specific tests are new
        is_old_cache_format = len(previous_passing_ids) == 0 and previous > 0

        try:
            # Get all passing features (uses internal endpoint without 5-feature cap)
            data = _api_get("/features/all-passing")
            for feature in data.get("features", []):
                feature_id = feature.get("id")
                current_passing_ids.append(feature_id)
                # Only identify individual new tests if we have previous IDs to compare
                if not is_old_cache_format and feature_id not in previous_passing_ids:
                    # This feature is newly passing
                    name = feature.get("name", f"Feature #{feature_id}")
                    category = feature.get("category", "")
                    if category:
                        completed_tests.append(f"{category} {name}")
                    else:
                        completed_tests.append(name)
        except Exception as e:
            print(f"[API error getting features: {e}]")

        payload = {
            "event": "test_progress",
            "passing": passing,
            "total": total,
            "percentage": round((passing / total) * 100, 1) if total > 0 else 0,
            "previous_passing": previous,
            "tests_completed_this_session": passing - previous,
            "completed_tests": completed_tests,
            "project": project_dir.name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps([payload]).encode("utf-8"),  # n8n expects array
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"[Webhook notification failed: {e}]")

        # Update cache with count and passing IDs
        cache_file.write_text(
            json.dumps({"count": passing, "passing_ids": current_passing_ids})
        )
    else:
        # Update cache even if no change (for initial state)
        if not cache_file.exists():
            current_passing_ids = []
            try:
                data = _api_get("/features/all-passing")
                for feature in data.get("features", []):
                    current_passing_ids.append(feature.get("id"))
            except Exception:
                pass
            cache_file.write_text(
                json.dumps({"count": passing, "passing_ids": current_passing_ids})
            )


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_tests(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        print(f"\nProgress: {passing}/{total} tests passing ({percentage:.1f}%)")
        send_progress_webhook(passing, total, project_dir)
    else:
        print("\nProgress: No features in database yet")
