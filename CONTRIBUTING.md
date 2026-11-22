**VidSnapAI — Project Blueprint & Workflow**

---

## 1. High-Level Blueprint

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                            │
│   Home · Create · Gallery · About · (Login / Register – PR #7)      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLASK APP  (main.py)                             │
│  • UI routes (Jinja templates)                                      │
│  • Auth (session-based – coming in PR #7)                           │
│  • Job API  /api/v1/jobs  (create · status · download)              │
│  • CSRF · Origin checks · Upload validation · Rate limits/quotas    │
└──────────┬───────────────────────────────┬──────────────────────────┘
           │                               │
           │  enqueue job                  │  presigned upload/download
           ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│  PostgreSQL / SQLite │        │  Object Storage      │
│  • users             │        │  (local or S3)       │
│  • video_jobs        │        │  inputs/ + outputs/  │
│  • reels metadata    │        └──────────────────────┘
└──────────┬───────────┘
           │  claim_next_job()
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 WORKER  (worker.py)  — persistent process            │
│  Poll DB → claim job → download inputs → run pipeline → upload MP4  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MEDIA PIPELINE  (pipeline/)                      │
│                                                                     │
│  text_to_audio.py  ──►  ElevenLabs TTS  ──►  audio.mp3              │
│         │                                                           │
│         ▼                                                           │
│  whisper_subtitles.py  ──►  word-level timings  ──►  SRT data       │
│         │                                                           │
│  beat_sync.py  ──►  music beat detection  ──►  image durations      │
│         │                                                           │
│  audio_processing.py  ──►  voice + music mix + ducking              │
│         │                                                           │
│  transitions.py  ──►  zoom/pan + xfade filter graph                 │
│         │                                                           │
│  video_processing.py  ──►  FFmpeg (libx264, crf 18)  ──►  final.mp4 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

| Layer | Files / Modules | Responsibility |
|-------|------------------|----------------|
| **Web / API** | `main.py`, `templates/`, `static/` | UI, auth, job enqueue, gallery |
| **Job system** | `production/jobs.py` | Queue, claim, progress, finish/fail |
| **Storage** | `production/storage.py` | Local or S3-compatible put/get + presign |
| **Worker** | `worker.py` | Long-running poller; only place that renders |
| **TTS** | `text_to_audio.py` | ElevenLabs voiceover |
| **Subtitles** | `pipeline/whisper_subtitles.py` | Whisper timestamps |
| **Beat sync** | `pipeline/beat_sync.py` | Music-aware image durations |
| **Audio mix** | `pipeline/audio_processing.py` | Ducking + normalization |
| **Visuals** | `pipeline/transitions.py` | Zoom/pan + xfade |
| **Export** | `pipeline/video_processing.py` | Final FFmpeg command |
| **Security** | `security_utils.py` | Extensions, UUID checks, bounded numbers |

---

## 3. End-to-End Workflow (Target – after hardening)

```
1. User registers / logs in
          │
2. Opens /create → uploads images + enters text prompt
          │
3. Frontend (or form) builds a manifest:
     { text, inputs: [{key, filename, duration}], settings }
          │
4. POST /api/v1/jobs
     • Auth required
     • Rate limit + daily quota checked
     • Job row created (status = queued)
          │
5. Worker (python worker.py) polls DB
     • claim_next_job() → status = running
          │
6. Worker pipeline:
     a. Download input images from storage
     b. ElevenLabs → audio.mp3
     c. Whisper → subtitle timings
     d. Beat detection → adjust image durations
     e. Mix voice + music (ducking)
     f. Build FFmpeg filter graph (transitions)
     g. Render high-quality MP4
     h. Upload MP4 → storage (outputs/{user}/{job}.mp4)
     i. finish_job() → status = succeeded
          │
7. User polls GET /api/v1/jobs/{id}
     • Sees progress / stage
          │
8. When succeeded → GET /api/v1/jobs/{id}/download
     • Receives short-lived signed URL
          │
9. Video also appears in Gallery (metadata + file)
```

---

## 4. Data Flow (simplified)

```
Images + Text
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Manifest   │────►│  video_jobs  │────►│   Worker    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    ▼               ▼           ▼           ▼               ▼
               TTS (ElevenLabs)  Whisper   Beat Sync   Audio Mix      FFmpeg
                    │               │           │           │               │
                    └───────────────┴───────────┴───────────┴───────────────┘
                                                │
                                                ▼
                                         final_reel.mp4
                                                │
                                                ▼
                                    Storage + Gallery + Download URL
```

---

## 5. Job State Machine

```
queued ──► running ──► succeeded
              │
              ├──► queued (retry, attempt < max)
              └──► failed  (attempts exhausted)
```

Fields tracked: `progress`, `stage`, `attempt_count`, `lease_expires_at`, `output_key`, `error_code`.

---

## 6. Local Development Workflow

```bash
# Terminal 1 – Web app
python main.py

# Terminal 2 – Worker (required for real generation)
python worker.py

# Optional: Docker worker
docker build -f Dockerfile.worker -t vidsnapai-worker .
docker run --rm --env-file .env vidsnapai-worker
```

**Required env (minimum):**
- `FLASK_SECRET_KEY`
- `ELEVENLABS_API_KEY`
- `DATABASE_URL` (or SQLite default)
- Storage settings if using S3 mode

---

## 7. Current vs Target Architecture

| Aspect | Current (master) | Target (PR #7 + Phase 1) |
|--------|------------------|---------------------------|
| Auth | None | Session register/login |
| Generation | Sync path still exists | Worker-only |
| Quotas | None | Daily + burst limits |
| FFmpeg | `shell=True` string | Safer arg list + logging |
| CI | Unit + lint | + FFmpeg smoke render |
| Identity for jobs | Placeholder | Real `session["user_id"]` |

---

## 8. Folder Map (mental model)

```
VidSnapAI-Piyu24/
├── main.py                 # Flask app + routes + job API
├── worker.py               # Persistent job runner
├── generate_process.py     # Legacy / shared reel builder
├── text_to_audio.py        # ElevenLabs bridge
├── pipeline/               # Core media engine
│   ├── video_processing.py
│   ├── audio_processing.py
│   ├── transitions.py
│   ├── beat_sync.py
│   ├── subtitles.py
│   └── whisper_subtitles.py
├── production/             # Durable infrastructure
│   ├── jobs.py
│   └── storage.py
├── templates/ + static/    # Frontend
├── Documentation/          # ARCHITECTURE, API, USAGE…
└── tests/                  # Unit + API + (soon) render tests
```

---

This is the living blueprint of the project. Once PR #7 lands, the “Target” column becomes the real runtime path.

Want me to also generate a clean visual architecture diagram image you can drop into the README, or a Mermaid version you can paste into GitHub?
