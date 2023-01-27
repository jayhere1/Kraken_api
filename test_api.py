import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from main import (base_url, get_outages, get_site_info, headers,
                  post_site_outages)


@pytest.mark.asyncio
async def test_get_outages():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/outages", headers=headers, ssl=False) as response:
            assert response.status == 200
            outages = await response.json()
            assert list(outages[0].keys()) == ["id", "begin", "end"]


@pytest.mark.asyncio
async def test_get_outages_retries(monkeypatch):
    async def mock_get(*args, **kwargs):
        mock_response = MagicMock()
        return mock_response

    monkeypatch.setattr(aiohttp.ClientSession, "get", AsyncMock(return_value=mock_get()))
    with pytest.raises(Exception, match="Maximum retries exceeded"):
        await get_outages(max_retries=1)


@pytest.mark.asyncio
async def test_get_site_info():
    site_info = await get_site_info("norwich-pear-tree")
    assert list(site_info.keys()) == ["id", "name", "devices"]


@pytest.mark.asyncio
async def test_get_site_info_retries(monkeypatch):
    @pytest.mark.asyncio
    async def mock_get(*args, **kwargs):
        mock_response = MagicMock()
        return mock_response

    monkeypatch.setattr(aiohttp.ClientSession, "get", AsyncMock(return_value=mock_get()))
    with pytest.raises(Exception, match="Maximum retries exceeded"):
        await get_site_info("norwich-pear-tree", max_retries=1)

    site_info = await get_site_info("kingfisher")
    assert site_info == "Site not found"


@pytest.mark.asyncio
async def test_post_site_outages():
    # test for successful post request
    site_id = "norwich-pear-tree"
    post_info = await post_site_outages(site_id)
    assert list(post_info[0].keys()) == ["id", "begin", "end", "name"]


@pytest.mark.asyncio
async def test_post_site_outages_typeerror():
    with pytest.raises(TypeError):
        site_id = "ABC"
        await post_site_outages(site_id)


# @patch("aiohttp.ClientSession.post")
# async def test_post_site_outages_mock(mock: CoroutineMock, aiohttp_client: TestClient) -> None:
#     # Create a mock object that represents an asynchronous context manager
#     # mock_post = AsyncMock()
#     # mock_post.return_value.__aenter__.return_value.status = 200
#     # mock_post.return_value.__aenter__.return_value.json.return_value = {"message": "Success"}

#     # # Use the patch() function to patch the aiohttp.ClientSession.post method
#     # with patch("aiohttp.ClientSession.post", mock_post):
#     #     site_id = "norwich-pear-tree"
#     #     outages = await post_site_outages(site_id)
#     #     assert outages == {"message": "Success"}

#     returned_data = {"key": "value"}
#     mock.return_value.__aenter__.return_value.json = CoroutineMock(
#         side_effect=lambda: returned_data
#     )

#     app = web.Application()
#     web_client = await aiohttp_client(app)

#     response: ClientResponse = await web_client.get("/path")
#     assert response.status == 200

#     assert mock.called
#     assert mock.call_count == 1
