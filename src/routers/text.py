from typing import List
from fastapi import APIRouter, HTTPException
from model import Text
import database as db

router = APIRouter()

@router.on_event("startup")
async def startup():
    await db.PoolProvider.init_pool()


@router.on_event("shutdown")
async def shutdown():
    await db.PoolProvider.close_pool()



@router.post("/texts/", response_model=Text)
async def create_text_endpoint(text: Text):
    try:
        return await db.create_text(db.PoolProvider.pool, text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/texts/", response_model=List[Text])
async def read_texts_endpoint():
    try:
        texts = await db.read_texts(db.PoolProvider.pool)
        return [Text(**text) for text in texts]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/texts/{text_id}", response_model=Text)
async def read_text_endpoint(text_id: int):
    try:
        text = await db.read_text(db.PoolProvider.pool, text_id)
        if text is None:
            raise HTTPException(status_code=404, detail="Text not found")
        return Text(**text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/texts/{text_id}", response_model=Text)
async def update_text_endpoint(text_id: int, updated_text: Text):
    try:
        text = await db.update_text(db.PoolProvider.pool, text_id, updated_text)
        if text is None:
            raise HTTPException(status_code=404, detail="Text not found")
        return Text(**text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/texts/{text_id}", response_model=dict)
async def delete_text_endpoint(text_id: int):
    try:
        await db.delete_text(db.PoolProvider.pool, text_id)
        return {"detail": "Text deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))