import json
import unittest

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from production.jobs import (
    JobError, claim_next_job, create_job_model, enqueue_job, fail_job,
    finish_job, init_jobs, update_job_progress,
)


class JobLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", SQLALCHEMY_TRACK_MODIFICATIONS=False)
        self.db = SQLAlchemy(self.app)
        init_jobs(self.db)
        self.Job = create_job_model(self.db)
        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def test_enqueue_and_idempotent_reuse(self):
        with self.app.app_context():
            job, created = enqueue_job(self.Job, "user-1", {"text": "hello", "inputs": ["x"]}, "key-1")
            again, created_again = enqueue_job(self.Job, "user-1", {"text": "ignored", "inputs": ["y"]}, "key-1")
            self.assertTrue(created)
            self.assertFalse(created_again)
            self.assertEqual(job.id, again.id)
            self.assertEqual(job.status, "queued")

    def test_job_claim_progress_and_success(self):
        with self.app.app_context():
            job, _ = enqueue_job(self.Job, "user-1", {"text": "hello"})
            claimed = claim_next_job(self.Job)
            self.assertEqual(claimed.id, job.id)
            self.assertEqual(claimed.status, "running")
            update_job_progress(self.Job, job.id, "Rendering", 65)
            finished = finish_job(self.Job, job.id, "outputs/user-1/job.mp4")
            self.assertEqual(finished.status, "succeeded")
            self.assertEqual(finished.progress, 100)

    def test_rejects_invalid_progress_and_output(self):
        with self.app.app_context():
            job, _ = enqueue_job(self.Job, "user-1", {"text": "hello"})
            claim_next_job(self.Job)
            with self.assertRaises(JobError):
                update_job_progress(self.Job, job.id, "bad", 100)
            with self.assertRaises(JobError):
                finish_job(self.Job, job.id, "")

    def test_retry_then_failure(self):
        with self.app.app_context():
            job, _ = enqueue_job(self.Job, "user-1", {"text": "hello"})
            claim_next_job(self.Job)
            failed = fail_job(self.Job, job.id)
            self.assertEqual(failed.status, "queued")
            failed.max_attempts = 1
            self.db.session.commit()
            claim_next_job(self.Job)
            failed = fail_job(self.Job, job.id)
            self.assertEqual(failed.status, "failed")

    def test_public_dict_omits_manifest_and_owner(self):
        with self.app.app_context():
            job, _ = enqueue_job(self.Job, "private-user", {"secret": "no"})
            public = job.public_dict()
            self.assertNotIn("input_manifest", public)
            self.assertNotIn("user_id", public)


if __name__ == "__main__":
    unittest.main()
