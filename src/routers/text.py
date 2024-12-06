import os
import json
from typing import List

from redis import asyncio as aioredis
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from model import Text, TextWrite
import database as db

router = APIRouter()

if os.path.exists('.env'):
    load_dotenv()

REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"


async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url(REDIS_URL)
    return redis


@router.on_event("startup")
async def startup():
    await db.PoolProvider.init_pool()


@router.on_event("shutdown")
async def shutdown():
    await db.PoolProvider.close_pool()


# @router.post("/texts/", response_model=Text)
# async def create_text_endpoint(text: TextWrite):
#     try:
#         return await db.create_text(db.PoolProvider.pool, text)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/texts/", response_model=List[Text])
async def read_texts_endpoint(redis: aioredis.Redis = Depends(get_redis)) -> List[Text]:
    try:
        cached_texts = await redis.get("text:all")
        if cached_texts:
            return JSONResponse(content=json.loads(cached_texts), status_code=200)

        texts = await db.read_texts(db.PoolProvider.pool)
        texts_model = [Text(**text) for text in texts]

        await redis.set("text:all", json.dumps([text.dict() for text in texts_model]))  

        return texts_model

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/texts/{text_id}", response_model=Text)
async def read_text_endpoint(
        text_id: int,
        redis: aioredis.Redis = Depends(get_redis)
    ) -> Text:
    try:

        cached_text = await redis.get(f"text:{text_id}")
        if cached_text:
            return JSONResponse(content=json.loads(cached_text), status_code=200)

        text = await db.read_text(db.PoolProvider.pool, text_id)
        if text is None:
            raise HTTPException(status_code=404, detail="Text not found")

        text_model = Text(**text)
        await redis.set(f"text:{text_id}", json.dumps(text_model.dict())) 

        return text_model

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.put("/texts/{text_id}", response_model=Text)
# async def update_text_endpoint(updated_text: Text):
#     try:
#         text = await db.update_text(db.PoolProvider.pool, updated_text)
#         if text is None:
#             raise HTTPException(status_code=404, detail="Text not found")
#         return Text(**text)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete("/texts/{text_id}", response_model=dict)
# async def delete_text_endpoint(text_id: int):
#     try:
#         await db.delete_text(db.PoolProvider.pool, text_id)
#         return {"detail": "Text deleted successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))