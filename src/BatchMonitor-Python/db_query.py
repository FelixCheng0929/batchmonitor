# -*- coding: utf-8 -*-
"""
db_query.py - SQLite interface for batch_execution monitoring.
Supports full sync + incremental via watermark, and job mapping lookup.
Stdlib only (sqlite3).
"""

import sqlite3
import json
import os
import logging

logger = logging.getLogger(__name__)


class WatermarkStore:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {"last_create_time": None, "initial_sync_done": False}

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.info("Watermark loaded: %s", self.data)
            except Exception as e:
                logger.warning("Watermark load failed: %s", e)

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        logger.debug("Watermark saved: %s", self.data)


class BatchExecutionDB:
    COLUMNS = [
        "id", "batch_id", "batch_name", "start_time", "end_time", "duration",
        "total_count", "success_count", "error_count", "warning_count",
        "result", "error_msg", "log_file", "exec_day_no", "create_time"
    ]

    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_full_sync_records(self):
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT " + ", ".join(self.COLUMNS) +
                " FROM batch_execution WHERE result IN ('\u7570\u5e38','\u8b66\u544a') ORDER BY create_time ASC"
            ).fetchall()
            logger.info("Full sync: %d records", len(rows))
            records = [dict(r) for r in rows]
            # Enrich with in_out from job mapping
            self._enrich_with_inout(records)
            return records
        finally:
            conn.close()

    def get_incremental_records(self, since_ct):
        conn = self._connect()
        try:
            sql = ("SELECT " + ", ".join(self.COLUMNS) +
                   " FROM batch_execution WHERE result IN ('\u7570\u5e38','\u8b66\u544a') AND create_time > ? ORDER BY create_time ASC")
            rows = conn.execute(sql, (since_ct,)).fetchall()
            records = [dict(r) for r in rows]
            max_ct = max((r["create_time"] for r in records if r["create_time"]), default=since_ct)
            logger.info("Incremental sync (since %s): %d records", since_ct, len(records))
            # Enrich with in_out from job mapping
            self._enrich_with_inout(records)
            return records, max_ct
        finally:
            conn.close()

    def get_max_create_time(self):
        conn = self._connect()
        try:
            row = conn.execute("SELECT MAX(create_time) FROM batch_execution").fetchone()
            return row[0] if row and row[0] else None
        finally:
            conn.close()

    # ── New: Lookup in_out from batch_info_master table ──────────────
    def get_in_out_by_job_id(self, job_id):
        """Look up the in_out value for a given job_id from batch_info_master.
        If multiple rows exist for the same job_id, prefers the one with exec_log='有'.
        Returns the in_out string (e.g. 'IN' / 'OUT') or None if not found.
        """
        conn = self._connect()
        try:
            # Prefer exec_log='有' when multiple rows match the same job_id
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='batch_info_master'").fetchone()
            if not row or row[0] == 0:
                return "查找表失败"
            row = conn.execute(
                "SELECT in_out FROM batch_info_master WHERE batch_id = ? ORDER BY CASE WHEN exec_log = '有' THEN 0 ELSE 1 END LIMIT 1",
                (job_id,)
            ).fetchone()
            return row[0] if row else "当前batch info 中无法找到匹配信息"
        finally:
            conn.close()

    def _enrich_with_inout(self, records):
        """Add 'in_out' key to each record dict by looking up batch_job_mapping."""
        for record in records:
            job_id = record.get("batch_id", "")
            if job_id:
                record["in_out"] = self.get_in_out_by_job_id(job_id)
            else:
                record["in_out"] = None
