from unittest.mock import AsyncMock, MagicMock

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
