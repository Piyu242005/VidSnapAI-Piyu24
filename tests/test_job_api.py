import unittest

from main import app


class JobApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_jobs_require_authenticated_server_identity(self):
        response = self.client.post("/api/v1/jobs", json={"manifest": {"text": "hello", "inputs": [{"key": "inputs/test.jpg"}]}})
        self.assertIn(response.status_code, (400, 401))

    def test_job_status_requires_authenticated_server_identity(self):
        response = self.client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
        self.assertEqual(response.status_code, 401)

    def test_download_requires_authenticated_server_identity(self):
        response = self.client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000/download")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
