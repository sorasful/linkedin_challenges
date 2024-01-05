import asyncio
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import httpx
from PIL import Image

BASE_URL = "https://www.pokecardex.com/assets/images/sets/XY/HD/"

# to avoid spamming the website and to have more determinstic response time
if os.getenv("IS_BENCHMARKING"):
    BASE_URL = "http://localhost:8000/assets/images/sets/XY/HD/"


NB_IMAGE_TO_DOWNLOAD = 20


def rgb_to_int(pixel: tuple[int, int, int]) -> int:
    """
    We move the pixels to the left to get a representation like this in binary :

    RRRRRRRRGGGGGGGGBBBBBBBB
    For example 255 0 255 will look like this

    0b111111110000000011111111

    Because we take the 255 turn into binary (11111111) move it 16 bytes to the left.
    We do the same for the Green and Blue but we move less, 8 bytes then 0 bytes so each component of
    the pixel get his own value. Then we calculate the sum we get an unique number for our RGB combination.
    """
    r, g, b = pixel
    return (r << 16) + (g << 8) + b


def int_to_rgb(value: int) -> tuple[int, int, int]:
    """
    Given a number, we take this number which is the sum of the RGB values.
    Remember the format looks like this :     0b111111110000000011111111
    So basically, we want to say :

    For Red, take the number and move 16 bytes to the left which will give us 0b11111111 then we apply a mask
    to only get the part that we are interested in.

    0xFF means 0b11111111  meaning that we only want to check our number for the last 8 bytes.

    For example 0b1111111111111001100 & 0xFF  -> will return me 204 because only the bytes with 1 in the mask
    are evaluated and since we look at the 8 first bytes we get 0b11001100 which is 204.


    We do the same for green and blue. Note that actually we could have omitted the mask for the Red color
    since the only bytes left are the one reprensenting this color.

    """

    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return r, g, b


async def get_image(url: str, client: httpx.AsyncClient) -> bytes:
    response = await client.get(url)
    assert response.status_code == 200

    return response.content


def get_most_present_pixels(image: bytes) -> Counter:
    img = Image.open(BytesIO(image), "r")
    most_common_pixels = Counter(rgb_to_int(pixel) for pixel in img.getdata())

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

    print(
        [
            (int_to_rgb(value), count)
            for value, count in aggregated_results.most_common(10)
        ]
    )


async def main() -> int:
    await get_most_common_pixels()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
