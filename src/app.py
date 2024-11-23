# main.py
from fastapi import FastAPI, HTTPException
from database import PoolProvider, write_answer
from model import Answer

app = FastAPI()


@app.on_event("startup")
async def startup():
    await PoolProvider.init_pool()


@app.on_event("shutdown")
async def shutdown():
    await PoolProvider.close_pool()


@app.post("/answers/", response_description="Добавить новый ответ")
async def create_answer(answer: Answer):
    """
    Эндпоинт для добавления нового ответа в базу данных.
    :param answer: Ответ, который нужно сохранить. 
                   Поля: user_id, text_id, difficult, interest.
    :return: Сообщение об успешном добавлении.
    """
    try:
        answer_id = await write_answer(PoolProvider.pool, answer)
        return {"answer_id": answer_id, "message": "Ответ успешно добавлен!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Для запуска приложения с uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
