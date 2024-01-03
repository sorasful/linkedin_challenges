import asyncio
import os
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import httpx
from PIL import Image

BASE_URL = "https://www.pokecardex.com/assets/images/sets/XY/HD/"

# to avoid spamming the website and to have more determinstic response time
if os.getenv("IS_BENCHMARKING"):
    BASE_URL = "http://localhost:8000/assets/images/sets/XY/HD/"


NB_IMAGE_TO_DOWNLOAD = 20


async def get_image(url: str, client: httpx.AsyncClient) -> bytes:
    response = await client.get(url)
    assert response.status_code == 200

    return response.content


def get_most_present_pixels(image: bytes) -> Counter:
    img = Image.open(BytesIO(image), "r")
    most_common_pixels = Counter(img.getdata())

    return most_common_pixels


async def get_most_common_pixels() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        get_image_tasks = [
            get_image(f"{BASE_URL}{i}.jpg", client=client)
            for i in range(1, NB_IMAGE_TO_DOWNLOAD + 1)
        ]

        images = await asyncio.gather(*get_image_tasks)

    aggregated_results = Counter()

    with ProcessPoolExecutor() as pool:
        for result in pool.map(get_most_present_pixels, images):
            aggregated_results.update(result)

    print(aggregated_results.most_common(10))


async def main() -> int:
    await get_most_common_pixels()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
