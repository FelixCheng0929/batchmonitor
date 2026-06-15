using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;

namespace BatchMonitor;

public class MonitorConfig
{
    public DatabaseConfig Database { get; set; } = new();
    public TeamsConfig Teams { get; set; } = new();
    public SyncConfig Sync { get; set; } = new();
}
public class DatabaseConfig
{
    [JsonPropertyName("searchPaths")] public List<string>? SearchPaths { get; set; }
    public string? Path { get; set; }
    [JsonPropertyName("search_paths")] private List<string>? S2 { set => SearchPaths ??= value; }
    [JsonPropertyName("path")] private string? P2 { set => Path ??= value; }
}
public class TeamsConfig
{
    [JsonPropertyName("alertTypes")] public List<string>? AlertTypes { get; set; }
    [JsonPropertyName("alert_types")] private List<string>? AT2 { set => AlertTypes ??= value; }
    [JsonPropertyName("webhooks")] public List<WebhookConfig>? Webhooks { get; set; }
    [JsonPropertyName("webhookUrl")] public string? WebhookUrl { get; set; }
    [JsonPropertyName("webhook_url")] private string? W2 { set => WebhookUrl ??= value; }
    [JsonPropertyName("excelBaseUrl")] public string? ExcelBaseUrl { get; set; }
    [JsonPropertyName("excel_base_url")] private string? E2 { set => ExcelBaseUrl ??= value; }
}
public class WebhookConfig { public string Name { get; set; } = ""; public string Url { get; set; } = ""; public bool Enabled { get; set; } = true; }
public class SyncConfig
{
    [JsonPropertyName("watermarkFile")] public string WatermarkFile { get; set; } = "sync_watermark.json";
    [JsonPropertyName("watermark_file")] private string? W2 { set => WatermarkFile ??= value ?? "sync_watermark.json"; }
    [JsonPropertyName("pollIntervalMinutes")] public int PollIntervalMinutes { get; set; } = 5;
    [JsonPropertyName("poll_interval_minutes")] private int? P2 { set => PollIntervalMinutes = (int)(value ?? 5); }
}
public class WatermarkData
{
    [JsonPropertyName("last_create_time")] public string? LastCreateTime { get; set; }
    [JsonPropertyName("initial_sync_done")] public bool InitialSyncDone { get; set; }
}
public class WatermarkStore
{
    private readonly string _p; private WatermarkData _d = new();
    public WatermarkStore(string p) { _p = p; Load(); }
    public void Load() { if (File.Exists(_p)) _d = JsonSerializer.Deserialize<WatermarkData>(File.ReadAllText(_p)) ?? new(); }
    public void Save() => File.WriteAllText(_p, System.Text.Json.JsonSerializer.Serialize((object)_d, new JsonSerializerOptions { WriteIndented = true }));
    public bool Done { get => _d.InitialSyncDone; set => _d.InitialSyncDone = value; }
    public string? Last { get => _d.LastCreateTime; set => _d.LastCreateTime = value; }
}
public class SentIdStore
{
    private readonly string _p; private HashSet<long> _ids = new();
    public SentIdStore(string p) { _p = p; Load(); }
    public void Load() { if (File.Exists(_p)) try { _ids = new(JsonSerializer.Deserialize<List<long>>(File.ReadAllText(_p)) ?? new()); } catch { } }
    public void Save() => File.WriteAllText(_p, System.Text.Json.JsonSerializer.Serialize((object)_ids.ToList(), new JsonSerializerOptions { WriteIndented = true }));
    public bool Sent(long id) => _ids.Contains(id);
    public void Mark(long id) { _ids.Add(id); if (_ids.Count > 10000) _ids = _ids.OrderByDescending(x => x).Take(10000).ToHashSet(); }
}
public class BatchExecutionRecord
{
    public long Id { get; set; } public string BatchId { get; set; } = "";
    public string? BatchName { get; set; } public string? StartTime { get; set; }
    public string? EndTime { get; set; } public long Duration { get; set; }
    public long TotalCount { get; set; } public long SuccessCount { get; set; }
    public long ErrorCount { get; set; } public long WarningCount { get; set; }
    public string Result { get; set; } = ""; public string? ErrorMsg { get; set; }
    public string? LogFile { get; set; } public long ExecDayNo { get; set; }
    public string? CreateTime { get; set; }
    public string? InOut { get; set; } // IN/OUT from batch_job_mapping
}
public class BatchExecutionDB
{
    private readonly string _cs;
    private static readonly string[] Cols = { "id","batch_id","batch_name","start_time","end_time","duration","total_count","success_count","error_count","warning_count","result","error_msg","log_file","exec_day_no","create_time" };
    private string C => string.Join(",", Cols);
    public BatchExecutionDB(string p) => _cs = $"Data Source={p};Version=3;";
    public (List<BatchExecutionRecord>, string?) Incremental(string? since, HashSet<string> types)
    {
        var ph = new List<string>(); var pm = new List<(string, object)>();
        for (int i = 0; i < types.Count; i++) { ph.Add($"@r{i}"); pm.Add(($"@r{i}", types.ElementAt(i))); }
        pm.Add(("@s", (object?)since ?? DBNull.Value));
        var sql = $"SELECT {C} FROM batch_execution WHERE result IN ({string.Join(",", ph)}) AND create_time>@s ORDER BY create_time ASC";
        var r = Q(sql, pm.ToArray());
        return (r, r.Any() ? r.Max(x => x.CreateTime) : since);
    }
    public string? MaxCt() { using var c = new SQLiteConnection(_cs); c.Open(); return new SQLiteCommand("SELECT MAX(create_time) FROM batch_execution", c).ExecuteScalar()?.ToString(); }
    // GetInOutByJobId - lookup IN/OUT from batch_job_mapping table, prefers exec_log='有'
    public string? GetInOutByJobId(string jobId)
    {
        using var c = new SQLiteConnection(_cs); c.Open();
        using var cmd = new SQLiteCommand("SELECT in_out FROM batch_job_mapping WHERE job_id = @jid ORDER BY CASE WHEN exec_log = '有' THEN 0 ELSE 1 END, no ASC LIMIT 1", c);
        cmd.Parameters.AddWithValue("@jid", jobId);
        var r = cmd.ExecuteScalar();
        return r?.ToString();
    }
    private List<BatchExecutionRecord> Q(string sql, params (string, object)[] p)
    {
        var l = new List<BatchExecutionRecord>();
        using var conn = new SQLiteConnection(_cs); conn.Open();
        using var cmd = new SQLiteCommand(sql, conn);
        foreach (var (n, v) in p) cmd.Parameters.AddWithValue(n, (object?)v ?? DBNull.Value);
        using var r = cmd.ExecuteReader();
        while (r.Read()) l.Add(new() { Id = r.GetInt64(0), BatchId = r.GetString(1), BatchName = r.IsDBNull(2) ? null : r.GetString(2), StartTime = r.IsDBNull(3) ? null : r.GetString(3), EndTime = r.IsDBNull(4) ? null : r.GetString(4), Duration = r.GetInt64(5), TotalCount = r.GetInt64(6), SuccessCount = r.GetInt64(7), ErrorCount = r.GetInt64(8), WarningCount = r.GetInt64(9), Result = r.GetString(10), ErrorMsg = r.IsDBNull(11) ? null : r.GetString(11), LogFile = r.IsDBNull(12) ? null : r.GetString(12), ExecDayNo = r.GetInt64(13), CreateTime = r.IsDBNull(14) ? null : r.GetString(14) });
        return l;
    }
}
public class TeamsSender
{
    public static async Task<bool> Send(string url, BatchExecutionRecord r, string? excelBaseUrl = null)
    {
        var jst = TimeZoneInfo.ConvertTime(DateTime.UtcNow, TimeZoneInfo.FindSystemTimeZoneById("Tokyo Standard Time"));
        var sync = jst.ToString("yyyy-MM-ddTHH:mm:ss");
        var color = "attention";
        var title = $"\ud83d\uded1 \u3010IF\u7570\u5e38\u5831\u544a\u3011 {r.BatchId}";
        var date = FmtDate(r.StartTime);
        var tr = $"{FmtTime(r.StartTime)} / {FmtTime(r.EndTime)}";
        var copyText = $"JOBID: {r.BatchId}\r\n\u65e5\u4ed8: {date}\r\n\u767a\u751f\u6642\u523b: {tr}\r\n\u7d50\u679c: \u7570\u5e38\r\n\u30a8\u30e9\u30fc\u4ef6\u6570: {r.ErrorCount}\r\n\u8b66\u544a\u4ef6\u6570: {r.WarningCount}\r\n\u5bfe\u8c61\u4ef6\u6570: {r.TotalCount}\r\n\u6210\u529f\u4ef6\u6570: {r.SuccessCount}\r\n\u6240\u8981\u6642\u9593: {r.Duration}s\r\n\u30ed\u30b0\u30d5\u30a1\u30a4\u30eb: {r.LogFile}\r\n\u540c\u671f\u77ac\u523b: {sync}";
        if (!string.IsNullOrEmpty(r.ErrorMsg)) copyText += $"\r\n\r\n\u3010\u7570\u5e38\u5185\u5bb9\u3011\r\n{r.ErrorMsg}";
        var recordPayload = new Dictionary<string, object?> { ["title"]=r.BatchId,["dbId"]=r.Id,["batchName"]=r.BatchName,["startTime"]=FmtDt(r.StartTime),["endTime"]=FmtDt(r.EndTime),["duration"]=r.Duration,["totalCount"]=r.TotalCount,["successCount"]=r.SuccessCount,["errorCount"]=r.ErrorCount,["warningCount"]=r.WarningCount,["result"]=r.Result,["errorMsg"]=r.ErrorMsg,["logFile"]=r.LogFile,["execDayNo"]=r.ExecDayNo,["syncTime"]=sync,["inOut"]=r.InOut };
        var body = new List<object> { new { type="TextBlock",text=title,weight="bolder",size="large",color,wrap=true }, new { type="TextBlock",text=copyText,wrap=true,spacing="medium",fontType="monospace" } };
        // Build record URL for Excel link
        var recordUrl = !string.IsNullOrEmpty(excelBaseUrl) ? $"{excelBaseUrl}?dbId={r.Id}" : "";
        var card = new Dictionary<string, object> { ["type"]="AdaptiveCard",["version"]="1.4",["body"]=body };
        if (!string.IsNullOrEmpty(recordUrl))
            card["actions"] = new object[] { new { type="Action.OpenUrl",title="\ud83d\udcc4 Open Record",url=recordUrl } };
        var payload = new { record = recordPayload, card };
        var json = System.Text.Json.JsonSerializer.Serialize((object)payload, new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping });
        using var h = new HttpClientHandler { ServerCertificateCustomValidationCallback = (_,_,_,_) => true };
        using var http = new HttpClient(h) { Timeout = TimeSpan.FromSeconds(15) };
        try { var resp = await http.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json")); return resp.IsSuccessStatusCode; }
        catch (Exception ex) { Console.WriteLine($"  [TEAMS] Error: {ex.Message}"); return false; }
    }
    private static string? FmtDate(string? dt) { if (string.IsNullOrEmpty(dt)) return ""; return dt.Length>=10 ? (dt.Contains(" ")?dt.Replace(" ","T")[..10]:dt[..10]).Replace("-","/") : ""; }
    private static string? FmtTime(string? dt) { if (string.IsNullOrEmpty(dt)) return ""; var s=dt.Contains(" ")?dt:dt.Replace("T"," "); return s.Contains(" ")?s.Substring(s.IndexOf(' ')+1,5):""; }
    private static string? FmtDt(string? dt) { if (string.IsNullOrEmpty(dt)) return null; var s=dt.Replace(" ","T");var d=s.IndexOf('.');return d>0?s[..d]:s; }
}
class Program
{
    static string LogFile = "monitor.log";
    static void Log(string msg) { var line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss}  {msg}"; Console.WriteLine(line); try { File.AppendAllText(LogFile, line + Environment.NewLine); } catch { } }
    static async Task<int> Main(string[] args)
    {
        var cp = "config_monitor.json"; var once = false;
        for (int i = 0; i < args.Length; i++) { if (args[i]=="--config" && i+1<args.Length) cp=args[++i]; if (args[i]=="--once") once=true; }
        if (!File.Exists(cp)) { Log("ERR: Config not found: "+cp); return 1; }
        var cfg = JsonSerializer.Deserialize<MonitorConfig>(File.ReadAllText(cp), new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;
        var cd = Path.GetDirectoryName(Path.GetFullPath(cp))!;
        var dp = ResolveDb(cfg, cd); if (dp==null) return 1;
        var urls = new List<string>();
        if (cfg.Teams.Webhooks!=null) foreach(var w in cfg.Teams.Webhooks) if(w.Enabled && !string.IsNullOrWhiteSpace(w.Url)) urls.Add(w.Url);
        if (urls.Count==0 && !string.IsNullOrEmpty(cfg.Teams.WebhookUrl)) urls.Add(cfg.Teams.WebhookUrl);
        if (urls.Count==0) { Log("ERR: No webhooks configured"); return 1; }
        var types = new HashSet<string>();
        foreach(var t in (cfg.Teams.AlertTypes??new List<string>{"abnormal"})) { var tl=t.Trim().ToLower(); if(tl=="abnormal") types.Add("\u7570\u5e38"); if(tl=="warning") types.Add("\u8b66\u544a"); }
        if (types.Count==0) types.Add("\u7570\u5e38");
        var wp = Path.IsPathRooted(cfg.Sync.WatermarkFile) ? cfg.Sync.WatermarkFile : Path.GetFullPath(Path.Combine(cd, cfg.Sync.WatermarkFile));
        var sp = Path.Combine(Path.GetDirectoryName(wp)??cd, "sent_ids.json");
        Log($"START DB:{dp} Alerts:[{string.Join(",",types)}] Webhooks:{urls.Count}");
        var db = new BatchExecutionDB(dp); var wm = new WatermarkStore(wp); var sid = new SentIdStore(sp);
        if (once) { await Run(db,wm,sid,urls,types,cfg.Teams.ExcelBaseUrl); return 0; }
        var iv = cfg.Sync.PollIntervalMinutes*60*1000;
        while(true) { try{await Run(db,wm,sid,urls,types,cfg.Teams.ExcelBaseUrl);}catch(Exception ex){Log("ERR: "+ex.Message);} await Task.Delay(iv); }
    }
    static async Task Run(BatchExecutionDB db, WatermarkStore wm, SentIdStore sid, List<string> urls, HashSet<string> types, string? eb)
    {
        if (!wm.Done) { wm.Done=true; wm.Last=db.MaxCt(); wm.Save(); Log($"INIT Watermark={wm.Last} Watching for [{string.Join(",",types)}]"); return; }
        var (recs,nw)=db.Incremental(wm.Last,types);
        if (recs.Any()){wm.Last=nw;wm.Save();}
        if (recs.Count==0){Log("POLL No new alerts");return;}
        Log($"ALERT {recs.Count} new record(s)");
        int sent=0,skip=0,fail=0;
        foreach(var r in recs)
        {
            // Populate InOut from batch_job_mapping
            if (!string.IsNullOrEmpty(r.BatchId))
                r.InOut = db.GetInOutByJobId(r.BatchId);

            if(sid.Sent(r.Id)){skip++;continue;}bool ok=false;foreach(var u in urls)ok|=await TeamsSender.Send(u,r,eb);if(ok){sid.Mark(r.Id);sent++;}else fail++;
        }
        sid.Save(); wm.Save();
        Log($"DONE Sent:{sent} Skipped:{skip} Failed:{fail}");
    }
    static string? ResolveDb(MonitorConfig cfg, string cd)
    {
        var c = new List<string>();
        if (cfg.Database.SearchPaths!=null) c.AddRange(cfg.Database.SearchPaths);
        if (!string.IsNullOrEmpty(cfg.Database.Path) && !c.Contains(cfg.Database.Path)) c.Add(cfg.Database.Path);
        foreach(var r in c){var p=Path.IsPathRooted(r)?Path.GetFullPath(r):Path.GetFullPath(Path.Combine(cd,r));if(File.Exists(p))return p;}
        Log("ERR: DB not found."); foreach(var r in c) Log("  "+(Path.IsPathRooted(r)?r:Path.GetFullPath(Path.Combine(cd,r)))); return null;
    }
}