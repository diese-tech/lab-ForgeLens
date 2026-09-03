# ForgeLens

ForgeLens is a **SMITE 2 league evidence and statistics bot** for Discord. It turns match screenshots and optional GodForge draft exports into organized, reviewable league data backed by Google Sheets and Drive.

Players provide evidence. ForgeLens fingerprints it, parses screenshots with Gemini Vision, links evidence to matches, writes normalized stat rows, and gives league staff explicit review and result-confirmation workflows.

> **Status:** Active MVP. Guild scoping, screenshot intake, OCR parsing, match lifecycle, Google Sheets/Drive output, and community-points ledger workflows are implemented. Deeper review tooling and durable economy storage remain ongoing work.

## What ForgeLens Owns

ForgeLens is the **evidence and stats companion**, not the live match-orchestration bot.

- **GodForge** owns live drafting, randomization, party/match orchestration, and portable Draft JSON handoff.
- **ForgeLens** owns screenshot evidence, OCR parsing, match/stat records, review state, reporting/export surfaces, and its guild-scoped community-points ledger.

ForgeLens can also operate standalone when GodForge is not installed.

## Core Capabilities

### Evidence and OCR

- Watches configured Discord channels for screenshots and compatible draft JSON
- Supports PNG, JPEG/JPG, GIF, and WebP evidence
- Uses SHA-256 fingerprints for duplicate protection
- Sends screenshots through Gemini Vision for scoreboard/details extraction
- Writes normalized match/stat rows to league-owned Google Sheets
- Keeps unlinked or partial evidence reviewable instead of silently discarding it
- Supports staff linking and reparsing workflows

### Match lifecycle

- Opens guild/channel-scoped match contexts
- Supports Bo1, Bo3, and Bo5 metadata
- Keeps GodForge draft data optional
- Uses explicit staff result confirmation before a match becomes official
- Prevents draft enrichment from becoming authoritative result data by itself

### Guild-scoped configuration

- Per-guild channels, season state, admin configuration, confidence metadata, Drive settings, and league prefixes
- Guild-scoped evidence, matches, wallets, wagers, and ledger records
- Compatibility migration from legacy active-season configuration

### Community points

ForgeLens includes a disabled-by-default fantasy points system with guild-scoped wallets, wagers, refunds, settlement, ledger transactions, and admin audit surfaces.

It is **community fantasy points only**. There is no real-money payment integration or gambling/compliance claim.

## Architecture

```text
Discord
  ├─ screenshots ──► evidence + Gemini OCR ──► Google Sheets / Drive
  ├─ Draft JSON ───► match enrichment ──────► Google Sheets / Drive
  └─ slash commands ─► match/config/economy services
```

Runtime configuration is scoped by Discord guild. Discord messages are evidence and interaction surfaces; normalized league data is written into the configured storage surfaces.

## Quick Start

Start with [`SETUP.md`](SETUP.md) for the complete Discord, Google Cloud, and Railway setup.

### Requirements

- Python 3.12, matching `runtime.txt`
- Discord bot token and required intents
- Google Cloud project with Gemini, Sheets, and Drive APIs enabled
- Google service-account credentials
- Gemini API key

### Install and run

```bash
pip install -r requirements.txt
python test_auth.py
python bot.py
```

Do not run ForgeLens for a real league until the Google authentication check passes.

For Railway, use environment variables rather than committing `.env` or credential files. The project supports `GOOGLE_CREDENTIALS_JSON` for hosted service-account configuration.

## Documentation

- [`SETUP.md`](SETUP.md) — full setup and deployment walkthrough
- `commands/` — current slash-command implementations
- `services/` — configuration, storage, evidence, match, and economy services

Use the runtime command registry and implementation as the final authority when older planning docs disagree with shipped behavior.

## Design Principles

- **Evidence first:** preserve source evidence and fingerprints so staff can review what produced a stat row.
- **Human authority:** OCR assists review; it does not silently become official league truth.
- **Guild isolation:** state from one Discord server must not leak into another.
- **Idempotent intake:** duplicate evidence should not create duplicate records.
- **Explicit result settlement:** community-point settlement requires an official linked match result.
- **Standalone capability:** GodForge integration should enrich ForgeLens, not become a hard dependency.
