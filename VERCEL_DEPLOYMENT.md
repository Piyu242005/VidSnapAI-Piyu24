# Vercel deployment (web preview)

VidSnapAI can run its Flask web interface on Vercel, but **the complete video-generation pipeline is not compatible with Vercel's short-lived serverless functions**. FFmpeg rendering, Whisper model inference, temporary uploads, and SQLite/local media storage need a persistent worker and durable storage.

## Deploy the web interface

1. Import `Piyu242005/VidSnapAI-Piyu24` into Vercel.
2. Keep the project root set to the repository root. The repository's `vercel.json` routes requests to the Flask WSGI app in `api/index.py`.
3. Add environment variables in Vercel Project Settings:
   - `FLASK_SECRET_KEY`: a long, random secret.
   - `ELEVENLABS_API_KEY`: a newly rotated key; never reuse a key that was committed to Git history.
   - `COOKIE_SECURE=1`
   - `TRUSTED_HOSTS`: your deployed Vercel hostname, e.g. `your-project.vercel.app`.
   - `DATABASE_URL`: optional external PostgreSQL URL if a persistent database is configured.
4. Deploy a Preview first and check the homepage, About, Features, and Gallery pages.

## Current limitations

- `/create` POST and `/api/preview-audio` return HTTP 503 on Vercel by design. This avoids pretending a long-running FFmpeg/Whisper task can reliably finish in a serverless request.
- Vercel's `/tmp` storage is temporary and instance-local. The fallback SQLite database and upload/reel paths are only for a short-lived preview, not durable user data.
- A real production setup needs a separate worker service for ElevenLabs + Whisper + FFmpeg, object storage for uploads/exports, a durable queue (for example Redis-backed jobs), and a shared managed database.
- Authentication/authorization, rate limiting, and a full end-to-end deployment test still need to be completed before public use.

## Local development

Run the app locally as documented in the main README. Local generation continues to use the local media pipeline.
