# -*- coding: utf-8 -*-
"""
init_job_mapping.py
===================
Initialize the batch_job_mapping table in the existing batch_monitor DB.
Creates table if not exists and inserts all job mapping data.

Usage:
    python init_job_mapping.py
    or specify: python init_job_mapping.py --db C:/path/to/crc_log_db.db
"""

import argparse
import json
import os
import sqlite3
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default search paths - same pattern as config_monitor.json
DEFAULT_SEARCH_PATHS = [
    "C:/source/monitor/v3/crc_log_db.db",
    "../crc_log_db.db",
]

# ── Table definition ──────────────────────────────────────────────
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS batch_job_mapping (
    no                  INTEGER PRIMARY KEY,
    job_id              TEXT    NOT NULL,
    name                TEXT,
    in_out              TEXT    NOT NULL,
    exec_log            TEXT,
    hogo_db_physical    TEXT,
    hogo_db_logical     TEXT,
    middle_table_physical TEXT,
    middle_table_logical  TEXT,
    d365_table_physical TEXT,
    d365_table_logical  TEXT
);
"""

# ── Data ──────────────────────────────────────────────────────────
# Columns: (no, job_id, name, in_out, exec_log)
# Note: job_id is NOT unique - MST_001 appears twice (no=4,5) with different exec_log.
# The lookup in db_query.py uses LIMIT 1, so both records exist but only the first
# match is returned per query. This is fine for in_out lookup since both have "IN".

DATA = [
    (1,   "Batch_001",        "作業指示連係後処理",                              "IN",    "有"),
    (2,   "File_001",         "入館PDFファイル連携IF",                          "IN",    "有"),
    (3,   "file_monitor",     "",                                                "OTHER", "有"),
    (4,   "MST_001",          "IN_作業先情報連携処理",                          "IN",    "有"),
    (5,   "MST_001",          "IN_作業先情報連携処理",                          "IN",    "無"),
    (6,   "MST_002",          "IN_セ＃情報連携処理",                            "IN",    "有"),
    (7,   "MST_003",          "IN_組織単位連携処理",                            "IN",    "有"),
    (8,   "MST_004",          "IN_リソース連携処理",                            "IN",    "有"),
    (9,   "MST_005",          "IN_安全ポイント情報連携処理",                     "IN",    "有"),
    (10,  "MST_006",          "IN_重点ポイント情報連携処理",                     "IN",    "有"),
    (11,  "MST_007",          "IN_連絡先情報連携処理",                          "IN",    "有"),
    (12,  "MST_008",          "IN_セ＃別階床情報詳細情報連携処理",              "IN",    "有"),
    (13,  "MST_011",          "IN_製品情報連携処理",                            "IN",    "有"),
    (14,  "MST_012",          "IN_鍵保管場所連携処理",                          "IN",    "有"),
    (15,  "MST_013",          "IN_鍵情報連携処理",                              "IN",    "有"),
    (16,  "MST_015",          "IN_ロープ寿命項目マスタ連携処理",                 "IN",    "有"),
    (17,  "MST_017",          "IN_インシデント種類情報連携処理",                 "IN",    "有"),
    (18,  "MST_020",          "IN_測定値形式ID翻訳マスター連携処理",             "IN",    "有"),
    (19,  "MST_021_01",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (20,  "MST_021_02",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (21,  "MST_021_11",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (22,  "MST_021_13",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (23,  "MST_021_15",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (24,  "MST_021_20",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (25,  "MST_021_30",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (26,  "MST_021_40",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (27,  "MST_021_50",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (28,  "MST_021_60",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (29,  "MST_021_70",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (30,  "MST_021_80",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (31,  "MST_021_90",       "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (32,  "MST_021_Morning",  "IN_測定値基準表連携_昇降機連携",                 "IN",    "有"),
    (33,  "MST_035",          "IN_測定値形式ID翻訳マスター連携処理",             "IN",    "有"),
    (34,  "MST_040",          "IN_レポート郵送管理報告先設定情報登録",           "IN",    "有"),
    (35,  "MST_042",          "IN_拠点翻訳連携処理",                            "IN",    "有"),
    (36,  "MST_044",          "IN_指示書用付加部位名翻訳マスタ連携処理",         "IN",    "有"),
    (37,  "MST_047",          "IN_部位名称翻訳マスタ連携処理",                   "IN",    "有"),
    (38,  "MST_049",          "IN_測定値基準表連携_冷熱連携",                   "IN",    "有"),
    (39,  "MST_050",          "IN_受電支援者連携",                              "IN",    "有"),
    (40,  "SFDC_001",         "緊急発報情報連携処理",                            "OTHER", "有"),
    (41,  "TRN_004",          "OUT_修理部品手配データ情報連携処理",              "OUT",   "有"),
    (42,  "TRN_005",          "IN_修理部品手配データ情報連携処理",               "IN",    "有"),
    (43,  "TRN_006",          "IN_予約情報連携処理",                            "IN",    "有"),
    (44,  "TRN_007",          "IN_作業指示書",                                  "IN",    "有"),
    (45,  "TRN_008",          "出発帰着情報連携処理_OUT",                        "OUT",   "有"),
    (46,  "TRN_009",          "OUT_入退館情報連携処理",                          "OUT",   "有"),
    (47,  "TRN_010",          "OUT_場所変更履歴連携処理",                        "OUT",   "有"),
    (48,  "TRN_011",          "OUT_鍵束利用管理情報連携処理",                   "OUT",   "有"),
    (49,  "TRN_012",          "OUT_鍵束合わせ情報連携処理",                      "OUT",   "有"),
    (50,  "TRN_013",          "OUT_鍵合わせ情報連携処理",                        "OUT",   "有"),
    (51,  "TRN_014",          "IN_申し送り事項連携処理",                        "IN",    "有"),
    (52,  "TRN_015",          "OUT_重点管理連携処理",                            "OUT",   "有"),
    (53,  "TRN_016",          "IN_重点管理連携処理",                            "IN",    "有"),
    (54,  "TRN_017",          "IN_ロープ寿命情報連携処理",                      "IN",    "有"),
    (55,  "TRN_018",          "OUT_修理作業情報連携処理",                        "OUT",   "有"),
    (56,  "TRN_019",          "IN_修理作業情報連携処理",                        "IN",    "有"),
    (57,  "TRN_020",          "IN_ステップ脱着ヘッダー情報連携処理",             "IN",    "有"),
    (58,  "TRN_021",          "OUT_ステップ脱着ヘッダー情報連携処理",            "OUT",   "有"),
    (59,  "TRN_022",          "OUT_ステップ脱着履歴連携",                        "OUT",   "有"),
    (60,  "TRN_023",          "IN_ステップ脱着履歴連携",                        "IN",    "有"),
    (61,  "TRN_024",          "OUT_走行時間連携処理",                            "OUT",   "有"),
    (62,  "TRN_025",          "IN_走行時間連携処理",                            "IN",    "有"),
    (63,  "TRN_026",          "OUT_起動回数実績連携処理",                        "OUT",   "有"),
    (64,  "TRN_027",          "IN_起動回数連携処理",                            "IN",    "有"),
    (65,  "TRN_028",          "OUT_作業先実績連携処理",                          "OUT",   "有"),
    (66,  "TRN_030",          "IN_作業履歴連携処理",                            "IN",    "有"),
    (67,  "TRN_031",          "IN_作業指示書インシデント情報連携",               "IN",    "有"),
    (68,  "TRN_032",          "IN_作業指示書タスク情報連携処理",                 "IN",    "有"),
    (69,  "TRN_034",          "IN_レポート次回作業予定連携処理",                 "IN",    "無"),
    (70,  "TRN_036",          "昇降機レポート号機グループマスタ情報連携_IN",     "IN",    "有"),
    (71,  "TRN_050",          "IN_メンテナンスレポート顧客名連携処理",           "IN",    "有"),
    (72,  "TRN_051",          "IN_レポート用ヘリオス測定値マスタ連携処理",       "IN",    "有"),
    (73,  "TRN_069",          "IN_冷熱レポート号機グループマスタ連携処理",       "IN",    "有"),
    (74,  "TRN_084",          "ソリューションレポート出力号機グループマスタ情報連携_IN", "IN", "有"),
    (75,  "TRN_087",          "IN_非継続作＃連携処理",                          "IN",    "有"),
    (76,  "TRN_090",          "IN_活動履歴",                                    "IN",    "有"),
    (77,  "TRN_092",          "OUT_RAKY連携",                                   "OUT",   "有"),
    (78,  "TRN_093",          "OUT_4RKYミーテング",                             "OUT",   "有"),
    (79,  "TRN_094",          "IN_個別指示連携処理",                            "IN",    "有"),
    (80,  "TRN_097",          "OUT_改善作業情報連携処理",                        "OUT",   "有"),
    (81,  "TRN_098",          "IN_改善作業情報連携処理",                        "IN",    "有"),
    (82,  "TRN_101",          "OUT_測定値記録表ボディ_昇降機連携処理",           "OUT",   "有"),
    (83,  "TRN_103",          "IN_資格情報連携処理",                            "IN",    "有"),
    (84,  "TRN_104",          "OUT_個別指示実績連携処理",                        "OUT",   "有"),
    (85,  "TRN_105",          "IN_ヘリオス検知情報連携処理",                    "IN",    "有"),
    (86,  "TRN_106",          "OUT_ヘリオス検知履歴連携処理",                    "OUT",   "有"),
    (87,  "TRN_107",          "OUT_重点管理修理計画連携",                        "OUT",   "有"),
    (88,  "TRN_108",          "IN_重点管理修理計画連携",                        "IN",    "有"),
    (89,  "TRN_110",          "OUT_ブレーキ電流変化データ連携",                  "OUT",   "有"),
    (90,  "TRN_111",          "IN_ブレーキ電流チェッカー連携処理",               "IN",    "有"),
    (91,  "TRN_112",          "OUT_ハンドレールマグネットモニター連携処理",       "OUT",   "有"),
    (92,  "TRN_113",          "IN_ハンドレールマグネットモニター連携処理",        "IN",    "有"),
    (93,  "TRN_115",          "OUT_チェックシート写真データ連携処理",            "OUT",   "有"),
    (94,  "TRN_115_2",        "OUT_チェックシート写真データ連携処理",            "OUT",   "有"),
    (95,  "TRN_116",          "申し送り事項連携処理_OUT",                        "OUT",   "有"),
    (96,  "TRN_118",          "修理履歴マスター修理実績情報連携_OUT",            "OUT",   "有"),
    (97,  "TRN_119",          "OUT_測定値記録表ヘッダ＆ボディ_冷熱連携処理",     "OUT",   "有"),
    (98,  "TRN_120",          "OUT_HRエックス線診連携",                          "OUT",   "有"),
    (99,  "TRN_121",          "IN_ブレーキ制動力診断連携処理",                   "IN",    "有"),
    (100, "TRN_124",          "OUT_クリート面浮き上がり検知連携処理",            "OUT",   "有"),
    (101, "TRN_126",          "OUT_ブレーキ制動力診断連携処理",                  "OUT",   "有"),
    (102, "TRN_127",          "IN_ロープ診断連携処理",                          "IN",    "有"),
    (103, "TRN_128",          "OUT_液晶CPI点検完了登録連携処理",                 "OUT",   "有"),
    (104, "TRN_129",          "OUT_レポートファイル連携",                        "OUT",   "有"),
    (105, "TRN_130",          "OUT_ロープ診断連携処理",                          "OUT",   "有"),
    (106, "TRN_131",          "OUT_Mg.B動作診断連携処理",                       "OUT",   "有"),
    (107, "TRN_132",          "IN_スケジュール作成連携処理",                    "IN",    "有"),
    (108, "TRN_133",          "IN_作業指示書状態変更",                          "IN",    "有"),
    (109, "TRN_134",          "OUT_昇降機レポート連携情報",                      "OUT",   "有"),
    (110, "TRN_135",          "OUT_冷熱レポート連携",                            "OUT",   "有"),
    (111, "TRN_136",          "OUT_ソリューションレポート連携",                  "OUT",   "有"),
    (112, "TRN_137",          "IN_冷凍機マスタ連携処理",                        "IN",    "有"),
    (113, "TRN_138",          "修理交換部品連携_OUT",                            "OUT",   "有"),
    (114, "TRN_140",          "作業実績情報連携（緊急）_OUT",                    "OUT",   "有"),
    (115, "TRN_141",          "IN_応援者職制連携処理",                          "IN",    "有"),
    (116, "TRN_142",          "IN_営業所住所処理",                              "IN",    "有"),
    (117, "TRN_143",          "OUT_Mg.B動作診断連携処理",                       "OUT",   "有"),
    (118, "TRN_144",          "OUT_ディスクブレーキ制動力試験連携処理",          "OUT",   "有"),
    (119, "TRN_145",          "IN_GMS割付変更連携",                             "IN",    "有"),
    (120, "TRN_146",          "OUT_メンテナンスツールメニュー",                  "OUT",   "有"),
    (121, "TRN_201",          "IN_起動回数管理連携処理",                        "IN",    "無"),
]

# Index on job_id for faster lookups
CREATE_INDEX_SQL = "CREATE INDEX IF NOT EXISTS idx_job_mapping_job_id ON batch_job_mapping(job_id);"


def find_db(search_paths, config_path=None):
    """Find the SQLite DB file using the same logic as batch_monitor.py"""
    candidates = list(search_paths)
    if config_path:
        cfg_dir = os.path.dirname(os.path.abspath(config_path))
        for raw in search_paths:
            r = os.path.normpath(raw if os.path.isabs(raw) else os.path.join(cfg_dir, raw))
            if os.path.exists(r):
                return r
    for raw in candidates:
        r = os.path.normpath(raw if os.path.isabs(raw) else os.path.join(SCRIPT_DIR, raw))
        if os.path.exists(r):
            return r
    # Last resort: try paths from config_monitor.json
    config_paths = [
        os.path.join(SCRIPT_DIR, "config_monitor.json"),
        os.path.join(os.path.dirname(SCRIPT_DIR), "config_monitor.json"),
    ]
    for cp in config_paths:
        if os.path.exists(cp):
            with open(cp, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            db_paths = cfg.get("database", {}).get("searchPaths", cfg.get("database", {}).get("search_paths", []))
            db_path = cfg.get("database", {}).get("path")
            if db_path and db_path not in db_paths:
                db_paths.append(db_path)
            cfg_dir = os.path.dirname(os.path.abspath(cp))
            for raw in db_paths:
                r = os.path.normpath(raw if os.path.isabs(raw) else os.path.join(cfg_dir, raw))
                if os.path.exists(r):
                    return r
    return None


def main():
    parser = argparse.ArgumentParser(description="Initialize batch_job_mapping table")
    parser.add_argument("--db", default=None, help="Path to SQLite DB file (crc_log_db.db)")
    args = parser.parse_args()

    # Find the DB
    db_path = args.db
    if not db_path:
        db_path = find_db(DEFAULT_SEARCH_PATHS)

    if not db_path:
        print("ERROR: Could not locate the database file.")
        print("Please specify with: python init_job_mapping.py --db <path_to_db>")
        print("Tried paths:")
        for raw in DEFAULT_SEARCH_PATHS:
            r = os.path.normpath(raw if os.path.isabs(raw) else os.path.join(SCRIPT_DIR, raw))
            print(f"  - {r}")
        sys.exit(1)

    print(f"Database: {db_path}")

    # Connect and create table + insert data
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Create table
        print("\n[1/4] Creating table batch_job_mapping...")
        cur.execute(CREATE_TABLE_SQL)
        print("  OK - Table ready (or already exists)")

        # Create index
        print("\n[2/4] Creating index on job_id...")
        cur.execute(CREATE_INDEX_SQL)
        print("  OK - Index ready")

        # Check existing data by primary key (no)
        cur.execute("SELECT COUNT(*) FROM batch_job_mapping")
        existing = cur.fetchone()[0]
        print(f"\n[3/4] Existing records: {existing}")

        # Check which 'no' values already exist
        cur.execute("SELECT no FROM batch_job_mapping")
        existing_nos = set(row[0] for row in cur.fetchall())

        new_rows = [r for r in DATA if r[0] not in existing_nos]
        skipped_rows = [r for r in DATA if r[0] in existing_nos]

        if new_rows:
            insert_sql = """
                INSERT OR IGNORE INTO batch_job_mapping
                    (no, job_id, name, in_out, exec_log,
                     hogo_db_physical, hogo_db_logical,
                     middle_table_physical, middle_table_logical,
                     d365_table_physical, d365_table_logical)
                VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL)
            """
            cur.executemany(insert_sql, new_rows)
            conn.commit()
            print(f"\n[4/4] Inserted {len(new_rows)} new record(s)")
        else:
            print(f"\n[4/4] No new records to insert (all {len(DATA)} already exist)")

        if skipped_rows:
            print(f"  Skipped (already exist by No): {len(skipped_rows)} record(s)")

        # Verify
        cur.execute("SELECT COUNT(*) FROM batch_job_mapping")
        total = cur.fetchone()[0]
        print(f"\nTotal records in batch_job_mapping: {total}")

        # Show stats
        cur.execute("SELECT in_out, COUNT(*) FROM batch_job_mapping GROUP BY in_out")
        print("\nBreakdown by in_out:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")

        # Show sample
        print("\nSample data (first 5):")
        cur.execute("SELECT no, job_id, name, in_out, exec_log FROM batch_job_mapping ORDER BY no LIMIT 5")
        for row in cur.fetchall():
            print(f"  No={row[0]}, job_id={row[1]}, name={row[2]}, in_out={row[3]}, exec_log={row[4]}")

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

    print("\n=== DONE ===")
    print("batch_job_mapping table is ready.")


if __name__ == "__main__":
    main()
