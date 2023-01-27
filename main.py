import asyncio
import datetime
import json
import logging
from pprint import pprint
from typing import List
from urllib.parse import urljoin

import aiohttp
import pytz
import yaml
from dateutil import parser
from fastapi import FastAPI

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

with open("api-key.txt") as f:
    passwd = f.readline()

base_url = "https://api.krakenflex.systems/interview-tests-mock-api/v1"

headers = {
    "accept": "application/json",
    "x-api-key": f"{passwd}",
}

app = FastAPI()

@app.get("/outages")
async def get_outages(max_retries=5, timeout=60):
    delay = 1
    retries = 0
    while retries < int(max_retries):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{base_url}/outages", headers=headers, ssl=False
                ) as response:
                    if response.status == 200:
                        outages = await response.json()
                        return outages
                    elif response.status == 500:
                        raise Exception("Server Error")
                    else:
                        raise Exception(f"status_code={response.status}, detail={response.text}")
            except Exception as e:
                log.error(e)
                retries += 1
                if retries < max_retries:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, timeout)
                else:
                    raise Exception("Maximum retries exceeded")

@app.get("/site/{site_id}")
async def get_site_info(
    site_id: str,
    max_retries=5,
    timeout=60,
):
    if site_id == "norwich-pear-tree":
        delay = 1
        retries = 0
        while retries < max_retries:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{base_url}/site-info/{site_id}", headers=headers, ssl=False
                    ) as response:
                        if response.status == 200:
                            outages = await response.json()
                            return outages
                        elif response.status == 500:
                            raise Exception("Server Error")
                        else:
                            raise Exception(
                                f"status_code={response.status}, detail={response.text}"
                            )
                except Exception as e:
                    log.error(e)
                    retries += 1
                    if retries < max_retries:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, timeout)
                    else:
                        raise Exception("Maximum retries exceeded")
    else:
        return "Site not found"

@app.post("/site/{site_id}/outages")
async def post_site_outages(site_id: str):
    outages = await get_outages()
    site_info = await get_site_info(site_id)

    devices = site_info["devices"]
    device_ids = [device["id"] for device in devices]

    filtered_outages = [
        outage
        for outage in outages
        if (
            parser.parse(outage["begin"]) >= pytz.UTC.localize(datetime.datetime(2022, 1, 1, 0, 0))
            and outage["id"] in device_ids
        )
    ]
    for outage in filtered_outages:
        device = next(device for device in devices if device["id"] == outage["id"])
        outage["name"] = device["name"]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/site-outages/{site_id}",
            json=(filtered_outages),
            headers=headers,
            ssl=False,
        ) as response:
            response.raise_for_status()
            outages = await response.json()
        if response.status != 200:
            raise Exception(f"status_code={response.status}, detail={response.text}")
    return filtered_outages


# print(asyncio.run(get_outages()))
# print(asyncio.run(get_site_info("norwich-pear-tree")))
if __name__ == "__main__":
    asyncio.run(post_site_outages("norwich-pear-tree"))
