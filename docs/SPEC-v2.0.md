# SPEC-20260611: BatchMonitor v2.0

## Goal
Upgrade BatchMonitor to support multiple Teams webhooks, configurable alert types, copy-to-clipboard, and production-ready deployment.

## Scope
- **In:** Multi-webhook support, config-based alert filtering (abnormal/warning on/off), AdaptiveCard with copy action, Python+NET dual versions, flexible poll interval
- **Out:** Dashboard UI, database write-back, historical replay

## Requirements

### R1: Multi-Webhook Config
Config supports an array of webhooks with name/enabled flags. All enabled webhooks receive alerts simultaneously.

### R2: Alert Type Filter
Config controls which result types trigger alerts. Default: only abnormal. Warning can be enabled via config.

### R3: AdaptiveCard with Copy Button
Each card includes an Action.Submit button. When clicked, copies all card text to clipboard. Card also includes timestamp, batch info, error details.

### R4: Card Design
Same format: 【IF異常報告】 header, JOBID, date, time range, result, error/warning counts, total/success counts, duration, log file, sync time, error message block.

### R5: Configurable Poll Interval
pollIntervalMinutes in config, default 5. VM Task Scheduler triggers accordingly.

### R6: Idempotent Delivery
sent_ids.json tracks delivered DB ids, watermark persists across restarts, no duplicates.

## Acceptance Criteria
- AC1: Multiple enabled webhooks in config -> all receive the same AdaptiveCard
- AC2: Config has alertTypes: ["abnormal"] -> only abnormal records trigger alerts
- AC3: Config has alertTypes: ["abnormal","warning"] -> both types trigger
- AC4: Each card has a working copy button
- AC5: Poll interval 1-60 min configurable
- AC6: Zero new records -> zero messages sent

## Assumptions
- Power Automate workflow forwards the raw HTTP body to Teams channel
- VM is Windows JST timezone
- DB path is configured in config_monitor.json
- .NET self-contained exe runs on VM without extra runtime

## Performance
- Daily abnormal records: 10-88 (avg ~40)
- Per-record send time: ~0.5s to each webhook
- 5-min interval: 0-3 records per check
- Max cycle time: < 2s
- Recommended interval: 5-10 min