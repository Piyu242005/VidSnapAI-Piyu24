"""Persistent database-polled video worker.

Run only on a persistent worker host, not inside Vercel serverless functions.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import traceback
from pathlib import Path

from main import app, db
from production.jobs import (
    claim_next_job, create_job_model, fail_job, finish_job, init_jobs, update_job_progress,
)
from production.storage import storage_from_env

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("vidsnapai.worker")
init_jobs(db)
VideoJob = create_job_model(db)


def process_job(job, storage):
    """Download a job's manifest, render with the existing pipeline, upload output."""
    manifest = json.loads(job.input_manifest)
    if not isinstance(manifest, dict):
        raise ValueError("invalid_manifest")
    inputs = manifest.get("inputs")
    settings = manifest.get("settings", {})
    description = manifest.get("text")
    if not isinstance(inputs, list) or not inputs or not isinstance(description, str) or not description.strip():
        raise ValueError("invalid_manifest")
    with tempfile.TemporaryDirectory(prefix=f"vidsnap-{job.id}-") as temp_dir:
        work = Path(temp_dir)
        upload_dir = work / "user_uploads" / job.id
        upload_dir.mkdir(parents=True)
        (upload_dir / "desc.txt").write_text(description, encoding="utf-8")
        local_inputs = []
        with app.app_context():
            for index, entry in enumerate(inputs):
                if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
                    raise ValueError("invalid_manifest")
                suffix = Path(entry.get("filename", f"image-{index}.jpg")).suffix.lower()
                if suffix not in {".jpg", ".jpeg", ".png"}:
                    raise ValueError("invalid_image_type")
                target = upload_dir / f"image_{index}{suffix}"
                storage.get_file(entry["key"], str(target))
                from PIL import Image
                with Image.open(target) as image:
                    image.verify()
                duration = float(entry.get("duration", 2.0))
                if not 0.25 <= duration <= 30:
                    raise ValueError("invalid_duration")
                local_inputs.append((target, duration))
            input_txt = upload_dir / "input.txt"
            with input_txt.open("w", encoding="utf-8") as stream:
                for path, duration in local_inputs:
                    escaped = str(path).replace("'", "'\\''")
                    stream.write(f"file '{escaped}'\nduration {duration}\n")
            (upload_dir / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            update_job_progress(VideoJob, job.id, "Generating voiceover", 10)
            from text_to_audio import text_to_speech_file
            text_to_speech_file(description, job.id, voice_id=settings.get("voice_id", "pNInz6obpgDQGcFmaJgB"), speed=float(settings.get("voice_speed", 1)), output_path=str(upload_dir / "audio.mp3"))
            # generate_process currently resolves uploads relative to the repository directory.
            # Prepare a compatible temporary layout, then relocate all output paths explicitly.
            import generate_process
            output_dir = work / "static" / "reels"
            output_dir.mkdir(parents=True, exist_ok=True)
            # A worker should not change process-wide CWD; create_reel is refactored to accept paths.
            output_path = generate_process.create_reel(job.id, settings=settings, upload_root=str(work / "user_uploads"), reels_root=str(output_dir))
            if not output_path or not Path(output_path).is_file():
                raise RuntimeError("output_missing")
            # An MP4 should contain the ftyp atom near the start of the file.
            with open(output_path, "rb") as handle:
                header = handle.read(64)
            if b"ftyp" not in header:
                raise RuntimeError("output_not_mp4")
            update_job_progress(VideoJob, job.id, "Uploading video", 95)
            output_key = f"outputs/{job.user_id}/{job.id}.mp4"
            storage.put_file(output_key, str(output_path))
            finish_job(VideoJob, job.id, output_key)
            return output_key


def run_forever(poll_seconds: float = 3.0):
    with app.app_context():
        storage = storage_from_env()
        logger.info("VidSnapAI worker starting; polling every %.1f seconds", poll_seconds)
        while True:
            try:
                job = claim_next_job(VideoJob, lease_seconds=int(os.getenv("JOB_LEASE_SECONDS", "900")))
                if job is None:
                    db.session.remove()
                    time.sleep(poll_seconds)
                    continue
                job_id = job.id
                logger.info("claimed job_id=%s attempt=%s", job_id, job.attempt_count)
                try:
                    process_job(job, storage)
                    logger.info("completed job_id=%s", job_id)
                except Exception as exc:
                    logger.exception("job failed job_id=%s error_type=%s", job_id, type(exc).__name__)
                    db.session.rollback()
                    try:
                        fail_job(VideoJob, job_id, "processing_failed")
                    except Exception:
                        db.session.rollback()
                        logger.exception("failed to record job failure job_id=%s", job_id)
                finally:
                    db.session.remove()
            except Exception:
                db.session.rollback()
                logger.exception("worker polling error")
                time.sleep(max(5.0, poll_seconds))


if __name__ == "__main__":
    run_forever(float(os.getenv("WORKER_POLL_SECONDS", "3")))
