# Microsoft Teams Chat Scraper

> Automated extraction of Microsoft Teams chat histories via Selenium — with virtual DOM handling, deduplication, image download, and a Flask-based chat viewer.

---

## Background

Microsoft Teams renders chat messages through a virtual DOM — as you scroll, older messages are unloaded from memory. This makes standard scraping approaches fail: by the time you reach the top of a long chat, the bottom is already gone.

This tool solves that with an **incremental accumulation strategy**: messages are extracted and hashed on each scroll step, with only newly-seen messages added to the output. Duplicates introduced by re-rendering are caught via hash comparison before writing.

Built for personal productivity — extracting project discussions and decision trails from Teams for offline search and archiving.

---

## Features

- **Virtual scrolling support** — handles Teams' dynamic message loading across arbitrarily long chat histories
- **Hash-based deduplication** — prevents duplicate messages from virtual DOM re-renders; persists hashes across sessions so re-runs only capture new messages
- **Image and attachment extraction** — downloads embedded images (HTTP/HTTPS, blob URLs, base64); captures attachment metadata
- **Flexible chat selection** — individual, range, or all chats; search-by-name support
- **Auto Edge driver management** — detects Edge version, downloads matching msedgedriver automatically
- **Multiple export formats** — per-chat JSON + CSV, combined export files, image summary
- **Web-based chat viewer** — Flask app for browsing extracted chats in the browser with real-time search filtering

---

## How It Works

```
Microsoft Teams (Browser via Selenium)
          │
          ▼
  Open chat → Scroll up incrementally
          │
          ▼
  Extract visible messages each step
  (text, author, timestamp, images)
          │
          ▼
  Hash each message → compare against known hashes
  New only → append to accumulated output
          │
          ▼
  JSON + CSV export  →  Flask viewer
```

### Deduplication detail

Each message generates a SHA hash from `(author + timestamp + content)`. Hashes are written to `[chat_name]_hashes.txt` after each run. On re-run, existing hashes are loaded first — only messages with unseen hashes are extracted and saved.

---

## Requirements

- Python 3.6+
- Microsoft Edge browser
- Microsoft Teams account (SSO login — manual login required on first run)

```bash
pip install -r requirements.txt
```

Dependencies: `selenium`, `requests`, `flask`

---

## Usage

### Scraper

```bash
# Basic run
python teams_chat_scraper.py

# Headless mode (no browser window)
python teams_chat_scraper.py --headless

# Skip image downloads
python teams_chat_scraper.py --no-images

# Custom output directory
python teams_chat_scraper.py --output-dir my_export

# Auto-select all chats
python teams_chat_scraper.py --auto-select-all
```

**Chat selection format** (when prompted):
- Individual: `1,3,5`
- Range: `5-7`
- Combined: `1,3,5-7`
- All: `all`

### Data Cleaning

After scraping, clean the raw JSON output into a structured CSV:

```bash
python Clean_chat_data.py
```

Outputs `cleaned_chat_data_with_content.csv` with columns: Chat Name, Message ID, Author, Timestamp, Content, Attachments, Images.

### Chat Viewer

```bash
python visualize_chat.py
# Open http://localhost:5000
```

Browse extracted chats in the browser — sidebar navigation, real-time name filtering, inline image rendering, clickable links.

---

## Output Structure

```
teams_complete_export/
├── [ChatName]_[timestamp].json     # Per-chat raw messages
├── [ChatName]_[timestamp].csv      # Per-chat CSV
├── [ChatName]_hashes.txt           # Deduplication hashes (persisted)
├── teams_export_[timestamp].json   # Combined all-chats JSON
├── teams_export_[timestamp].csv    # Combined all-chats CSV
├── image_summary_[timestamp].json  # Image download stats
└── images/
    └── [ChatName]_[ImageHash].ext  # Downloaded images
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Browser automation | Selenium + Microsoft Edge WebDriver |
| Virtual scroll handling | Custom incremental scroll + hash accumulation |
| Data cleaning | Python (pandas, re, json) |
| Export formats | JSON, CSV |
| Chat viewer | Flask + Jinja2 + HTML/CSS/JS |

---

## Known Limitations

- **Manual login required** — SSO login must be completed in the browser window on first run; no credential storage
- **Embedded screenshots** — screenshots pasted directly into chats may not be extracted (known bug)
- **Very long chats** — extraction may stop early on extremely long histories (Teams UI instability)
- **Teams UI changes** — Selenium selectors may break if Microsoft updates the Teams web interface
- **Attachments** — file attachment metadata is captured but files are not downloaded

---

## Repo Structure

```
teams-chat-scraper/
├── README.md
├── requirements.txt
├── teams_chat_scraper.py    # Main scraper — TeamsCollector class
├── Clean_chat_data.py       # JSON → cleaned CSV pipeline
└── visualize_chat.py        # Flask chat viewer
```
