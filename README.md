# BatchMonitor

Batch execution monitor for D365 Field Service integration workflows.
Detects abnormal/warning batch execution records and sends alerts to Teams via webhook.

## Features
- Monitor batch_execution table for abnormal/warning records
- Look up IN/OUT type from batch_job_mapping table
- Send structured alerts to Teams via webhook (AdaptiveCard format)
- Idempotent delivery (watermark + sent ID tracking)
- Configurable poll interval and alert types
- Multi-webhook support
- Single-file self-contained executable (no .NET runtime required on VM)

## Repository Structure

```
batchmonitor/
├── src/
│   ├── BatchMonitor/        # .NET source code (main executable)
│   ├── BatchMonitor-Python/ # Python reference version
│   └── InitDB/              # .NET source code (DB init tool)
├── deploy/
│   └── BatchMonitor-v3.0-deploy.zip  # Pre-built deploy package
├── docs/
│   └── SPEC-v2.0.md         # Specification document
└── README.md
```

## Quick Start

### 1. Initialize mapping table (first time only)
```bash
InitDB.exe
```

### 2. Run monitor
```bash
BatchMonitor.exe --once    # Single scan
BatchMonitor.exe           # Daemon mode (every 5 min)
```

## Changelog
- v3.0: Added batch_job_mapping table, InOut field in Teams webhook payload
- v2.0: Multi-webhook, AdaptiveCard, configurable alert types
- v1.0: Initial release, Teams webhook integration
