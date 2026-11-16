# -*- coding: utf-8 -*-
"""
VerseNest Originals - Automated Song Discovery Scheduler
Runs periodic background scans using MusicBrainz and authorized feeds.
Supports standalone daemon loop and one-off CLI execution.
"""
import time
import argparse
from discovery import run_discovery_pipeline

def run_scheduled_job(interval_hours: int = 24, max_artists_per_run: int = 5):
    """Runs periodic legal song discovery at regular intervals."""
    print(f"[Scheduler] Starting automated discovery daemon (Interval: {interval_hours}h)...")
    while True:
        try:
            print(f"[Scheduler] Executing scheduled discovery job at {time.ctime()}...")
            report = run_discovery_pipeline(source_name="Scheduled Daily Job", max_artists=max_artists_per_run)
            print(f"[Scheduler] Job finished successfully: {report['total_candidates']} candidates processed, "
                  f"{report['imported_count']} new, {report['duplicates_skipped']} duplicates skipped, "
                  f"{report['review_queued']} queued for review.")
        except Exception as e:
            print(f"[Scheduler] Error during scheduled discovery: {e}")

        # Sleep until next scheduled interval
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VerseNest Periodic Discovery Job")
    parser.add_argument("--once", action="store_true", help="Run once and exit immediately")
    parser.add_argument("--interval", type=int, default=24, help="Interval in hours (default: 24)")
    parser.add_argument("--artists", type=int, default=4, help="Max artists to query per run")
    args = parser.parse_args()

    if args.once:
        print("[Scheduler] Running one-off discovery job...")
        rep = run_discovery_pipeline(source_name="Manual CLI Run", max_artists=args.artists)
        print("Run Complete:", rep)
    else:
        run_scheduled_job(interval_hours=args.interval, max_artists_per_run=args.artists)
