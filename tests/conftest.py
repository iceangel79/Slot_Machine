"""Test setup: the API tests use a separate test database (decision 0015).

The tests read TEST_DATABASE_URL (local: from .env, a Neon branch "test";
CI: the PostgreSQL service container) and point the application to it before
it is imported. Without TEST_DATABASE_URL the API tests are not collected, so
they can never write into the production database by accident.
"""

import os

from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if TEST_DATABASE_URL:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    collect_ignore = []
else:
    collect_ignore = ["test_api.py"]


def pytest_report_header():
    if TEST_DATABASE_URL:
        return "API tests: using TEST_DATABASE_URL"
    return "API tests: SKIPPED (TEST_DATABASE_URL not set)"
