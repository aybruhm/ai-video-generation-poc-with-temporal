import asyncio
import uuid

import aiohttp

API_URL = "http://localhost:1459/api/"
HEADERS = {"Content-Type": "application/json"}


async def test_server_connection():
    async with aiohttp.ClientSession(
        base_url=API_URL,
        headers=HEADERS,
    ) as session:
        async with session.get("health") as resp:
            return resp.status == 200


async def register_user(*, username: str, password: str):
    async with aiohttp.ClientSession(
        base_url=API_URL,
        headers=HEADERS,
    ) as session:
        async with session.post(
            "auth/register",
            json={
                "username": username,
                "password": password,
            },
        ) as resp:
            return await resp.json()


async def login_user(username: str, password: str):
    async with aiohttp.ClientSession(
        base_url=API_URL,
        headers=HEADERS,
    ) as session:
        async with session.post(
            "auth/login",
            json={
                "username": username,
                "password": password,
            },
        ) as resp:
            return await resp.json()


async def main():
    username = str(uuid.uuid4())[:6]
    password = str(uuid.uuid4())

    print(
        "============================================================================"
    )
    print("Testing server connection...")
    if await test_server_connection():
        print("Server is up and running.")
    else:
        print("Server is not responding.")
        return

    user = await register_user(username=username, password=password)
    print(
        "=============================================================================="
    )
    print(f"Account created for {user['username']}")
    print(f"Logging in as {user['username']}...")
    print(
        "=============================================================================="
    )
    user_with_credentials = await login_user(username, password)
    print(f"Logged in as {user_with_credentials['user']['username']}")
    print(f"Access token: {user_with_credentials['credentials']['access_token']}")
    print(
        "=============================================================================="
    )
    return user_with_credentials["credentials"]["access_token"]


if __name__ == "__main__":
    asyncio.run(main())
