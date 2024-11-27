# main.py
from typing import List

from fastapi import FastAPI, HTTPException

import database as db
from model import Answer
from routers import text

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.PoolProvider.init_pool()


@app.on_event("shutdown")
async def shutdown():
    await db.PoolProvider.close_pool()


@app.post("/answers/", response_description="Добавить новый ответ")
async def create_answer(answer: Answer):
    """
    Добавление нового ответа в базу данных.
    :param answer: Ответ, который нужно сохранить. 
                   Поля: user_id, text_id, difficult, interest.
    :return: Сообщение об успешном добавлении.
    """
    try:
        answer_id = await db.write_answer(db.PoolProvider.pool, answer)
        return {"answer_id": answer_id, "message": "Ответ успешно добавлен!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/answers/user/{user_id}", response_model=List[Answer])
async def get_answers_by_user(user_id: int):
    """
    Получить все ответы пользователя по user_id.
    :param user_id: ID пользователя.
    :return: Список ответов пользователя.

    """
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id должен быть положительным")

    try:
        answers = await db.get_answers_by_user_id(db.PoolProvider.pool, user_id)
        return answers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/answers/text/{text_id}", response_model=List[Answer])
async def get_answers_by_text(text_id: int):
    """
    Получить все ответы пользователя по text_id.
    :param text_id: ID текста.
    :return: Список ответов по указанному text_id.
    """

    if text_id <= 0:
        raise HTTPException(status_code=400, detail="text_id должен быть положительным")

    try:
        answers = await db.get_answers_by_text_id(db.PoolProvider.pool, text_id)
        return answers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users/", response_description="Добавить нового пользователя")
async def add_user():
    """
    Добавление нового пользователя в базу данных.
    :return: {"user_id": user_id, "message": "Пользователь успешно добавлен!"}
    """
    try:
        user_id = await db.create_user(db.PoolProvider.pool)
        return {"user_id": user_id, "message": "Пользователь успешно добавлен!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(text.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
