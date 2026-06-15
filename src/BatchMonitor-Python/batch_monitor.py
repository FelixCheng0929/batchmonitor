# -*- coding: utf-8 -*-
"""batch_monitor.py - Teams-only monitor. Detect new abnormal/warning records, send to Teams webhook."""

import argparse, json, logging, os, sys, ssl, time, urllib.request, urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from db_query import BatchExecutionDB, WatermarkStore

def find_config(paths):
    for p in paths:
        if os.path.exists(p): return p
    print("ERR: Config not found."); sys.exit(1)

def resolve_db(cfg, cfg_dir):
    candidates = list(cfg.get("database", {}).get("searchPaths", cfg.get("database", {}).get("search_paths", [])))
    mp = cfg.get("database", {}).get("path")
    if mp and mp not in candidates: candidates.append(mp)
    for raw in candidates:
        r = os.path.normpath(raw if os.path.isabs(raw) else os.path.join(cfg_dir, raw))
        if os.path.exists(r): return r
    print("ERR: DB not found. Tried:"); [print("  "+os.path.normpath(raw if os.path.isabs(raw) else os.path.join(cfg_dir,raw))) for raw in candidates]; sys.exit(1)

def resolve(raw, cfg_dir):
    return os.path.normpath(raw if os.path.isabs(raw) else os.path.join(cfg_dir, raw))

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def send_teams(webhook_url, record):
    import time as tm
    jst = tm.localtime()
    sync_time = tm.strftime("%Y-%m-%dT%H:%M:%S", jst)
    payload = {
        "title": record.get("batch_id",""),
        "dbId": record.get("id"),
        "batchName": record.get("batch_name",""),
        "startTime": fmt_dt(record.get("start_time")),
        "endTime": fmt_dt(record.get("end_time")),
        "duration": record.get("duration",0),
        "totalCount": record.get("total_count",0),
        "successCount": record.get("success_count",0),
        "errorCount": record.get("error_count",0),
        "warningCount": record.get("warning_count",0),
        "result": record.get("result",""),
        "errorMsg": record.get("error_msg",""),
        "logFile": record.get("log_file",""),
        "execDayNo": record.get("exec_day_no",0),
        "syncTime": sync_time,
        "inOut": record.get("in_out"),   # <-- NEW: IN/OUT info from batch_job_mapping
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return resp.status in (200,202)
    except Exception as e:
        print(f"[TEAMS] Error: {e}")
        return False

def fmt_dt(dt):
    if not dt: return None
    s = str(dt).replace(" ", "T"); d = s.find(".")
    return s[:d] if d > 0 else s

class SentIdStore:
    def __init__(self, path):
        self.path = path; self.ids = set()
        if os.path.exists(path):
            try:
                with open(path,"r") as f: self.ids = set(json.load(f))
            except: pass
    def save(self):
        lst = sorted(self.ids, reverse=True)[:10000]
        with open(self.path,"w") as f: json.dump(lst, f)
    def already(self, i): return i in self.ids
    def mark(self, i): self.ids.add(i)

def run_cycle(db, wm, sent, webhook_url):
    if not wm.data.get("initial_sync_done"):
        logging.info("=== INITIAL SYNC ===")
        records = db.get_full_sync_records()
        logging.info("Found %d records", len(records))
        if records:
            s = 0; sk = 0
            for r in records:
                if sent.already(r["id"]): sk+=1; continue
                if send_teams(webhook_url, r): sent.mark(r["id"]); s+=1
            sent.save()
            logging.info("Sent: %d, Skipped: %d", s, sk)
        wm.data["initial_sync_done"] = True
        wm.data["last_create_time"] = db.get_max_create_time()
        wm.save()
        return

    records, new_wm = db.get_incremental_records(wm.data["last_create_time"])
    if records:
        wm.data["last_create_time"] = new_wm; wm.save()
    logging.info("Incremental: %d new", len(records))
    if records:
        s = 0; sk = 0
        for r in records:
            if sent.already(r["id"]): sk+=1; continue
            if send_teams(webhook_url, r): sent.mark(r["id"]); s+=1
        sent.save()
        logging.info("Sent: %d, Skipped: %d", s, sk)
    wm.save()

def main():
    parser = argparse.ArgumentParser(description="BatchMonitor (Teams)")
    parser.add_argument("--config", default=None)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    config_paths = [args.config] if args.config else []
    config_paths += [os.path.join(SCRIPT_DIR,"config_monitor.json"), os.path.join(os.path.dirname(SCRIPT_DIR),"config_monitor.json")]
    cp = find_config(config_paths)
    cfg_dir = os.path.dirname(os.path.abspath(cp))
    with open(cp,"r",encoding="utf-8") as f: cfg = json.load(f)

    setup_logging()
    logger = logging.getLogger("main")

    db_path = resolve_db(cfg, cfg_dir)
    webhook_url = cfg.get("teams",{}).get("webhookUrl", cfg.get("teams",{}).get("webhook_url",""))
    wm_path = resolve(cfg.get("sync",{}).get("watermarkFile","sync_watermark.json"), cfg_dir)
    sent_path = os.path.join(os.path.dirname(wm_path),"sent_ids.json")

    if not webhook_url:
        logger.error("teams.webhookUrl not configured"); sys.exit(1)

    logger.info("DB: %s", db_path)
    logger.info("Teams: configured")

    db = BatchExecutionDB(db_path)
    wm = WatermarkStore(wm_path); wm.load()
    sent = SentIdStore(sent_path)

    if args.once:
        run_cycle(db, wm, sent, webhook_url)
        return

    interval = cfg.get("sync",{}).get("pollIntervalMinutes",5) * 60
    logger.info("Polling every %d min", cfg.get("sync",{}).get("pollIntervalMinutes",5))
    while True:
        try: run_cycle(db, wm, sent, webhook_url)
        except Exception as e: logger.error("Cycle error: %s", e)
        logger.info("Next in %d min...", cfg.get("sync",{}).get("pollIntervalMinutes",5))
        time.sleep(interval)

if __name__ == "__main__":
    main()
