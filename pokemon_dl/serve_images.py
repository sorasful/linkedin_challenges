import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/assets/images/sets/{set_path:path}")
async def get_image(set_path: str) -> FileResponse:
    await asyncio.sleep(0)

    image_path = os.path.join("assets", "images", "sets", set_path)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404)

    return FileResponse(image_path)
