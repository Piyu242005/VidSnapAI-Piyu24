"""PostgreSQL-backed job lifecycle primitives for VidSnapAI.

The queue is deliberately database-backed for the low-cost first deployment.
Workers poll claim_next_job(); PostgreSQL row locks prevent duplicate claims.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Index, text
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

# Bind the application's SQLAlchemy extension with init_jobs(db).
db: SQLAlchemy | None = None


def init_jobs(database: SQLAlchemy) -> None:
    global db
    db = database


def _database():
    if db is None:
        raise RuntimeError("Job database is not initialized")
    return db


class JobError(ValueError):
    """Safe job validation or state-transition error."""


class Job:
    """Small namespace marker; ORM model is registered by create_job_model()."""


def create_job_model(database: SQLAlchemy):
    """Create the ORM model dynamically on the application's existing db."""
    class VideoJob(database.Model):
        __tablename__ = "video_jobs"
        __table_args__ = (
            Index("ix_video_jobs_status_created", "status", "created_at"),
        )

        id = database.Column(database.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = database.Column(database.String(128), nullable=False, index=True)
        status = database.Column(database.String(20), nullable=False, default="queued", index=True)
        input_manifest = database.Column(database.Text, nullable=False)
        progress = database.Column(database.Integer, nullable=False, default=0)
        stage = database.Column(database.String(80), nullable=False, default="Queued")
        attempt_count = database.Column(database.Integer, nullable=False, default=0)
        max_attempts = database.Column(database.Integer, nullable=False, default=3)
        idempotency_key = database.Column(database.String(128), nullable=True)
        output_key = database.Column(database.String(1024), nullable=True)
        error_code = database.Column(database.String(80), nullable=True)
        lease_expires_at = database.Column(database.DateTime(timezone=True), nullable=True)
        created_at = database.Column(database.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
        started_at = database.Column(database.DateTime(timezone=True), nullable=True)
        finished_at = database.Column(database.DateTime(timezone=True), nullable=True)
        updated_at = database.Column(database.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

        def public_dict(self):
            return {
                "id": self.id, "status": self.status, "progress": self.progress,
                "stage": self.stage, "attempt_count": self.attempt_count,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "error_code": self.error_code,
            }

    return VideoJob


def enqueue_job(model, user_id: str, input_manifest: dict, idempotency_key: str | None = None):
    if not user_id or len(user_id) > 128:
        raise JobError("invalid_user")
    if not isinstance(input_manifest, dict):
        raise JobError("invalid_manifest")
    payload = json.dumps(input_manifest, separators=(",", ":"), sort_keys=True)
    session = _database().session
    if idempotency_key:
        existing = model.query.filter_by(user_id=user_id, idempotency_key=idempotency_key).first()
        if existing:
            return existing, False
    job = model(user_id=user_id, input_manifest=payload, idempotency_key=idempotency_key)
    session.add(job)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        if idempotency_key:
            existing = model.query.filter_by(user_id=user_id, idempotency_key=idempotency_key).first()
            if existing:
                return existing, False
        raise
    return job, True


def claim_next_job(model, lease_seconds: int = 300):
    """Atomically claim the oldest eligible job; PostgreSQL required for concurrency."""
    database = _database()
    now = datetime.now(timezone.utc)
    # Lock and claim in one transaction so concurrent workers skip claimed rows.
    if database.engine.dialect.name != "postgresql":
        # SQLite path enables local development/testing but is not a multi-worker queue.
        job = model.query.filter_by(status="queued").order_by(model.created_at.asc()).first()
        if not job:
            return None
        job.status = "running"
        job.attempt_count += 1
        job.started_at = now
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.stage = "Starting"
        database.session.commit()
        return job
    row = database.session.execute(text("""
        SELECT id FROM video_jobs
        WHERE status = 'queued'
           OR (status = 'running' AND lease_expires_at < :now AND attempt_count < max_attempts)
        ORDER BY created_at
        FOR UPDATE SKIP LOCKED LIMIT 1
    """), {"now": now}).first()
    if row is None:
        database.session.rollback()
        return None
    job = model.query.filter_by(id=row[0]).with_for_update().one()
    job.status = "running"
    job.attempt_count += 1
    job.started_at = now
    job.lease_expires_at = now + timedelta(seconds=lease_seconds)
    job.stage = "Starting"
    job.error_code = None
    database.session.commit()
    return job


def update_job_progress(model, job_id: str, stage: str, progress: int, lease_seconds: int = 300):
    if not isinstance(progress, int) or not 0 <= progress <= 99:
        raise JobError("invalid_progress")
    job = model.query.filter_by(id=job_id).first()
    if job is None or job.status != "running":
        raise JobError("job_not_running")
    job.stage = str(stage)[:80]
    job.progress = progress
    job.lease_expires_at = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
    _database().session.commit()
    return job


def finish_job(model, job_id: str, output_key: str):
    job = model.query.filter_by(id=job_id).first()
    if job is None or job.status != "running":
        raise JobError("job_not_running")
    if not output_key or len(output_key) > 1024:
        raise JobError("invalid_output_key")
    job.status, job.progress, job.stage = "succeeded", 100, "Completed"
    job.output_key = output_key
    job.error_code = None
    job.finished_at = datetime.now(timezone.utc)
    job.lease_expires_at = None
    _database().session.commit()
    return job


def fail_job(model, job_id: str, error_code: str = "processing_failed"):
    job = model.query.filter_by(id=job_id).first()
    if job is None:
        raise JobError("job_not_found")
    job.error_code = "".join(c for c in error_code.lower() if c.isalnum() or c in "_-")[:80] or "processing_failed"
    job.lease_expires_at = None
    if job.attempt_count < job.max_attempts:
        job.status, job.stage = "queued", "Retry queued"
    else:
        job.status, job.stage = "failed", "Failed"
        job.finished_at = datetime.now(timezone.utc)
    _database().session.commit()
    return job
