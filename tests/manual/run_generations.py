import asyncio

import aiohttp

from tests.manual.create_account import main as entrypoint

API_URL = "http://localhost:1459/api/"
HEADERS = {
    "Content-Type": "application/json",
}


async def create_generation():
    access_token = await entrypoint()
    HEADERS["Cookie"] = f"access_token={access_token}"

    async with aiohttp.ClientSession(
        base_url=API_URL,
        headers=HEADERS,
    ) as session:
        payload = {
            "prompt": """Two person street interview in New York City.\nSample Dialogue:\nHost: 'Did you hear the news?'\nPerson: 'Yes! Veo 3.1 is now available on fal. If you want to see it, go check their website.'""",
            "model": "fal-ai/veo3.1/fast",
            "duration": "8s",
            "aspect_ratio": "16:9",
            "token_cost": 20,
        }
        async with session.post(
            "generations",
            json=payload,
        ) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                error_message = await response.text()
                print(f"Error: {e.status} - {error_message}")
                raise e
            return await response.json()


async def get_generation_status(generation_id: str):
    async with aiohttp.ClientSession(
        base_url=API_URL,
        headers=HEADERS,
    ) as session:
        async with session.get(
            f"generations/{generation_id}/status",
        ) as response:
            return await response.json()


async def main():
    print(
        "============================================================================"
    )
    result = await create_generation()
    print(
        f"Generation created: {result['generation_id']} - Status: {result['status']} - Workflow ID: {result['workflow_id']}"
    )
    print(
        "============================================================================"
    )
    print(f"Polling status for generation: {result['generation_id']}")
    while True:
        status = await get_generation_status(result["generation_id"])
        print(f"Status: {status['status']}")
        if str(status["status"]).lower() in ["completed", "failed"]:
            break
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
