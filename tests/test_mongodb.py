import pytest

from DB.mongodb import client


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connection():
    from DB.mongodb import client

    result = await client.admin.command("ping")
    assert result["ok"] == 1
