using System.Data.SQLite;

// ── Data ────────────────────────────────────────────────────────
// Columns: (no, job_id, name, in_out, exec_log)
var DATA = new (int no, string jobId, string name, string inOut, string execLog)[]
{
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
};

// ── Main ────────────────────────────────────────────────────────
Console.WriteLine("=== InitDB: Initialize batch_job_mapping table ===");

// Find database
var dbPath = args.Length > 0 ? args[0] : null;
if (string.IsNullOrEmpty(dbPath))
{
    var candidates = new[] {
        @"C:\source\monitor\v3\crc_log_db.db",
        "..\\crc_log_db.db",
        ".\\crc_log_db.db",
    };
    foreach (var c in candidates)
    {
        var p = Path.GetFullPath(c);
        if (File.Exists(p)) { dbPath = p; break; }
    }
    // Try config_monitor.json
    if (string.IsNullOrEmpty(dbPath))
    {
        foreach (var configPath in new[] { "config_monitor.json", "..\\config_monitor.json" })
        {
            var fp = Path.GetFullPath(configPath);
            if (File.Exists(fp))
            {
                try
                {
                    var json = File.ReadAllText(fp);
                    var cfg = System.Text.Json.JsonSerializer.Deserialize<System.Text.Json.JsonElement>(json);
                    if (cfg.TryGetProperty("database", out var db))
                    {
                        if (db.TryGetProperty("searchPaths", out var sp))
                        {
                            foreach (var s in sp.EnumerateArray())
                            {
                                var raw = s.GetString();
                                if (raw == null) continue;
                                var rp = Path.IsPathRooted(raw) ? raw : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(fp)!, raw));
                                if (File.Exists(rp)) { dbPath = rp; break; }
                            }
                        }
                        if (string.IsNullOrEmpty(dbPath) && db.TryGetProperty("path", out var pp))
                        {
                            var raw = pp.GetString();
                            if (!string.IsNullOrEmpty(raw))
                            {
                                var rp = Path.IsPathRooted(raw) ? raw : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(fp)!, raw));
                                if (File.Exists(rp)) dbPath = rp;
                            }
                        }
                    }
                }
                catch { }
                if (!string.IsNullOrEmpty(dbPath)) break;
            }
        }
    }
}

if (string.IsNullOrEmpty(dbPath) || !File.Exists(dbPath))
{
    Console.Error.WriteLine("ERROR: Database file not found.");
    Console.Error.WriteLine("Usage: InitDB.exe <path_to_crc_log_db.db>");
    return 1;
}

Console.WriteLine($"Database: {dbPath}");
var connStr = $"Data Source={dbPath};Version=3;";

try
{
    using var conn = new SQLiteConnection(connStr);
    conn.Open();

    // Create table
    Console.Write("[1/4] Creating table batch_job_mapping...");
    using (var cmd = new SQLiteCommand(@"
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
        )", conn))
    {
        cmd.ExecuteNonQuery();
    }
    Console.WriteLine(" OK");

    // Create index
    Console.Write("[2/4] Creating index...");
    using (var cmd = new SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_job_mapping_job_id ON batch_job_mapping(job_id)", conn))
    {
        cmd.ExecuteNonQuery();
    }
    Console.WriteLine(" OK");

    // Check existing
    Console.Write("[3/4] Checking existing data...");
    var existingNos = new HashSet<int>();
    using (var cmd = new SQLiteCommand("SELECT no FROM batch_job_mapping", conn))
    using (var r = cmd.ExecuteReader())
    {
        while (r.Read()) existingNos.Add(r.GetInt32(0));
    }
    Console.WriteLine($" {existingNos.Count} existing");

    // Insert new data
    Console.Write("[4/4] Inserting data...");
    using var tx = conn.BeginTransaction();
    var insertCmd = new SQLiteCommand(@"
        INSERT OR IGNORE INTO batch_job_mapping
            (no, job_id, name, in_out, exec_log,
             hogo_db_physical, hogo_db_logical,
             middle_table_physical, middle_table_logical,
             d365_table_physical, d365_table_logical)
        VALUES (@no, @job_id, @name, @in_out, @exec_log,
                NULL, NULL, NULL, NULL, NULL, NULL)", conn, tx);

    var pNo = insertCmd.Parameters.Add("@no", System.Data.DbType.Int32);
    var pJobId = insertCmd.Parameters.Add("@job_id", System.Data.DbType.String);
    var pName = insertCmd.Parameters.Add("@name", System.Data.DbType.String);
    var pInOut = insertCmd.Parameters.Add("@in_out", System.Data.DbType.String);
    var pExecLog = insertCmd.Parameters.Add("@exec_log", System.Data.DbType.String);

    int inserted = 0, skipped = 0;
    foreach (var d in DATA)
    {
        if (existingNos.Contains(d.no)) { skipped++; continue; }
        pNo.Value = d.no;
        pJobId.Value = d.jobId;
        pName.Value = string.IsNullOrEmpty(d.name) ? DBNull.Value : d.name;
        pInOut.Value = d.inOut;
        pExecLog.Value = d.execLog;
        insertCmd.ExecuteNonQuery();
        inserted++;
    }
    tx.Commit();
    Console.WriteLine($" {inserted} inserted, {skipped} skipped");

    // Summary
    using var sumCmd = new SQLiteCommand("SELECT in_out, COUNT(*) FROM batch_job_mapping GROUP BY in_out", conn);
    using var sumR = sumCmd.ExecuteReader();
    Console.WriteLine($"\nTotal: {inserted + skipped + existingNos.Count - skipped}");
    Console.WriteLine("Breakdown:");
    while (sumR.Read()) Console.WriteLine($"  {sumR.GetString(0)}: {sumR.GetInt32(1)}");

    Console.WriteLine("\n=== DONE ===");
}
catch (Exception ex)
{
    Console.Error.WriteLine($"\nERROR: {ex.Message}");
    return 1;
}

return 0;
