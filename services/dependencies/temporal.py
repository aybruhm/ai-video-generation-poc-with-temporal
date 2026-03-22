from temporalio.client import Client

from utils.env_utils import env


async def get_temporal_client():
    client = await Client.connect(target_host=env.TEMPORAL_TARGET_HOST)
    return client
