import pytest
from DB.mongodb import client

@pytest.mark.asyncio

async def test_connection():
    result = await client.admin.command("ping")
    assert result['ok'] == 1