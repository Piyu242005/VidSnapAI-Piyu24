import os
import shutil
import subprocess
import tempfile
import unittest

from main import app, db, User, VideoJob


class AuthAndJobTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        with app.app_context():
            db.session.query(VideoJob).delete()
            db.session.query(User).delete()
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.query(VideoJob).delete()
            db.session.query(User).delete()
            db.session.commit()
        app.config["WTF_CSRF_ENABLED"] = True
        app.config["TESTING"] = False

    def register(self, email):
        return self.client.post("/register", json={"email": email, "password": "test-pass-123"})

    def login(self, email):
        return self.client.post("/login", json={"email": email, "password": "test-pass-123"})

    def manifest(self):
        return {"manifest": {"text": "hello", "inputs": [{"key": "inputs/test.jpg", "duration": 1.0}]}}

    def test_register_login_logout(self):
        response = self.register("alice@example.com")
        self.assertEqual(response.status_code, 201)
        self.assertIn("user_id", response.get_json())
        self.client.post("/logout")
        response = self.login("alice@example.com")
        self.assertIn(response.status_code, (200, 302))
        response = self.client.post("/logout")
        self.assertIn(response.status_code, (200, 302))

    def test_jobs_require_authentication(self):
        self.assertEqual(self.client.post("/api/v1/jobs", json=self.manifest()).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/jobs/missing").status_code, 401)
        self.assertEqual(self.client.get("/api/v1/jobs/missing/download").status_code, 401)

    def test_job_create_and_ownership(self):
        self.register("alice@example.com")
        response = self.client.post("/api/v1/jobs", json=self.manifest())
        self.assertIn(response.status_code, (200, 202))
        job_id = response.get_json()["job_id"]
        self.assertEqual(self.client.get(f"/api/v1/jobs/{job_id}").status_code, 200)
        self.client.post("/logout")
        self.register("bob@example.com")
        self.assertEqual(self.client.get(f"/api/v1/jobs/{job_id}").status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/jobs/{job_id}/download").status_code, 404)

    def test_daily_quota_and_rate_limit(self):
        old_daily = os.environ.get("DAILY_JOB_LIMIT")
        old_rate = os.environ.get("JOB_CREATION_RATE_LIMIT")
        os.environ["DAILY_JOB_LIMIT"] = "1"
        os.environ["JOB_CREATION_RATE_LIMIT"] = "1"
        try:
            self.register("quota@example.com")
            self.assertIn(self.client.post("/api/v1/jobs", json=self.manifest()).status_code, (200, 202))
            response = self.client.post("/api/v1/jobs", json=self.manifest())
            self.assertEqual(response.status_code, 429)
            self.assertIn(response.get_json()["error"], ("quota_exceeded", "rate_limit_exceeded"))
        finally:
            if old_daily is None:
                os.environ.pop("DAILY_JOB_LIMIT", None)
            else:
                os.environ["DAILY_JOB_LIMIT"] = old_daily
            if old_rate is None:
                os.environ.pop("JOB_CREATION_RATE_LIMIT", None)
            else:
                os.environ["JOB_CREATION_RATE_LIMIT"] = old_rate


class FfmpegSmokeTests(unittest.TestCase):
    def test_minimal_color_render(self):
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            self.skipTest("FFmpeg is not installed")
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "smoke.mp4")
            command = [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:d=1",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", output]
            result = subprocess.run(command, shell=False, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, (result.stderr or "")[-4000:])
            self.assertTrue(os.path.isfile(output))


if __name__ == "__main__":
    unittest.main()
