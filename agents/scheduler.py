import json
import os
import threading
import time
from datetime import datetime

import schedule

from config import CACHE_DIR

_LOG_FILE = os.path.join(CACHE_DIR, "schedule_log.json")
_RESULTS_FILE = os.path.join(CACHE_DIR, "latest_results.json")
_scheduler_running = False
_scheduler_thread = None


def run_morning_analysis():
    from config import UNIVERSE
    from orchestrator import PortfolioOrchestrator

    log = {"timestamp": datetime.now().isoformat(), "status": "running", "tickers": []}
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        tickers = UNIVERSE["stocks"] + UNIVERSE["etfs"]
        log["tickers"] = tickers
        orch = PortfolioOrchestrator(tickers)
        results = orch.run_full_analysis(tickers)
        # Serialize without prices_df (not JSON serializable)
        serializable = {k: v for k, v in results.items() if k != "market"}
        market_copy = {k: v for k, v in results.get("market", {}).items() if k != "prices_df"}
        serializable["market"] = market_copy
        with open(_RESULTS_FILE, "w") as f:
            json.dump(serializable, f, default=str, indent=2)
        log["status"] = "success"
        log["report_path"] = results.get("report_path", "")
    except Exception as e:
        log["status"] = "error"
        log["error"] = str(e)

    history = []
    if os.path.exists(_LOG_FILE):
        try:
            with open(_LOG_FILE) as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(log)
    with open(_LOG_FILE, "w") as f:
        json.dump(history[-50:], f, indent=2)
    print(f"[Scheduler] Morning analysis {log['status']} at {log['timestamp']}")


def _scheduler_loop():
    while _scheduler_running:
        schedule.run_pending()
        time.sleep(30)


def start_scheduler(run_time="08:00"):
    global _scheduler_running, _scheduler_thread

    schedule.clear()
    schedule.every().day.at(run_time).do(run_morning_analysis)
    _scheduler_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
    print(f"[Scheduler] Started — daily analysis at {run_time}")


def get_scheduler_status():
    global _scheduler_running
    jobs = schedule.get_jobs()
    next_run = str(jobs[0].next_run)[:16] if jobs else "N/A"
    history = []
    if os.path.exists(_LOG_FILE):
        try:
            with open(_LOG_FILE) as f:
                history = json.load(f)
        except Exception:
            history = []
    return {
        "running": _scheduler_running,
        "next_run": next_run,
        "jobs": len(jobs),
        "log": history[-5:],
    }
