"""This module contains the healthcheck functionality.

It provides a mechanism for pinging an external healthcheck endpoint
every 15 minutes to verify that the application is still running.
"""

import asyncio
import requests
import os

# Default to a no-op URL if not specified
HEALTHCHECK_URL = os.environ.get("HEALTHCHECK_URL", "https://example.com/healthcheck")

async def healthcheck_ping():
    """Ping the healthcheck endpoint.

    This function will be called periodically to ping the healthcheck endpoint
    to verify that the application is still running.
    """
    try:
        response = requests.get(HEALTHCHECK_URL, timeout=10)
        print(f" [x] Healthcheck ping sent to {HEALTHCHECK_URL}, status: {response.status_code}")
        return True
    except Exception as e:
        print(f" [!] Error pinging healthcheck endpoint: {e}")
        return False

async def schedule_periodic_healthcheck(interval_seconds=900):  # 15 minutes = 900 seconds
    """Schedule periodic healthcheck pings.

    This function will schedule periodic healthcheck pings at the specified interval.
    """
    while True:
        await healthcheck_ping()
        await asyncio.sleep(interval_seconds)

def get_healthcheck_task():
    """Get the periodic healthcheck task.

    This function will return a coroutine that schedules periodic healthcheck pings.
    """
    return schedule_periodic_healthcheck()
