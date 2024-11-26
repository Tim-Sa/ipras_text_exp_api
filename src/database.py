import os
from typing import List, Optional
from dotenv import load_dotenv

import asyncpg
from model import Answer


class PoolProvider():
     pool = None

     @classmethod
     async def init_pool(cls):
        if cls.pool is None:
            cls.pool = await create_pool()

     @classmethod
     async def close_pool(cls):
        if cls.pool is not None:
            cls.pool.close()


if os.path.exists('.env'):
    load_dotenv()


def get_postgres_dsn():
    user = os.getenv('PSQL_DB_USERNAME')
    host = os.getenv('PSQL_DB_HOST', 'localhost')
    port = os.getenv('PSQL_DB_PORT', '5432')
    password = os.getenv('PSQL_DB_PASSWORD')
    database = os.getenv('PSQL_DB_DATABASE_NAME')

    if not all([user, password, database]):
        raise ValueError("Не все необходимые переменные окружения заданы")

    dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return dsn


dsn = get_postgres_dsn()


async def create_pool():
    return await asyncpg.create_pool(dsn)


async def is_text_exists(pool: any, text_id: int) -> bool:
    async with pool.acquire() as connection:
        text_exists = await connection.fetchval(
            'SELECT EXISTS(SELECT 1 FROM public.text WHERE text_id = $1)', text_id
        )
        return text_exists


async def is_user_exists(pool: any, user_id: int) -> bool:
    async with pool.acquire() as connection:
        user_exists = await connection.fetchval(
            'SELECT EXISTS(SELECT 1 FROM public.user WHERE user_id = $1)', user_id
        )
        return user_exists


async def write_answer(pool: any, answer: Answer) -> int:
    async with pool.acquire() as connection:
        query_insert = """
        INSERT INTO public.answer (user_id, text_id, difficult, interest)
        VALUES ($1, $2, $3, $4)
        RETURNING answer_id;
        """
        
        query_check_existence = """
        SELECT COUNT(*)
        FROM public.answer
        WHERE user_id = $1 AND text_id = $2;
        """

        is_exists = await is_text_exists(pool, answer.text_id)
        if not is_exists:
            raise ValueError("Text with provided id doesn't exists")

        is_exists = await is_user_exists(pool, answer.user_id)
        if not is_exists:
            raise ValueError("User with provided id doesn't exists")

        count = await connection.fetchval(query_check_existence, answer.user_id, answer.text_id)
        if count > 0:
            raise ValueError(f"Answer already exists for user_id {answer.user_id} and text_id {answer.text_id}")

        # If no existing answer, insert the new one
        answer_id = await connection.fetchval(query_insert, 
                                              answer.user_id, 
                                              answer.text_id, 
                                              answer.difficult, 
                                              answer.interest)

        return answer_id


async def get_answers_by_text_id(pool: any, text_id: int) -> List[Answer]:
    async with pool.acquire() as connection:
        query = """
        SELECT user_id, text_id, difficult, interest
        FROM public.answer
        WHERE text_id = $1;
        """

        is_exists = await is_text_exists(pool, text_id)
        if not is_exists:
            raise ValueError("Text with provided id doesn't exists")

        rows = await connection.fetch(query, text_id)
        answers = [Answer(**row) for row in rows]

        return answers


async def get_answers_by_user_id(pool: any, user_id: int) -> List[Answer]:
    async with pool.acquire() as connection:
        query = """
        SELECT user_id, text_id, difficult, interest
        FROM public.answer
        WHERE user_id = $1;
        """

        is_exists = await is_user_exists(pool, user_id)
        if not is_exists:
            raise ValueError("User with provided id doesn't exists")

        rows = await connection.fetch(query, user_id)
        answers = [Answer(**row) for row in rows]

        return answers


async def create_user(pool: any) -> int:
    async with pool.acquire() as connection:
        query_insert_user = """
        INSERT INTO public.user DEFAULT VALUES RETURNING user_id;
        """
        user_id = await connection.fetchval(query_insert_user)
        return user_id



async def read_texts(pool) -> List[dict]:
    async with pool.acquire() as connection:
        query = "SELECT * FROM texts;"
        rows = await connection.fetch(query)
        return [dict(row) for row in rows]


async def read_text(pool, text_id: int) -> Optional[dict]:
    async with pool.acquire() as connection:
        query = "SELECT * FROM texts WHERE id = $1;"
        row = await connection.fetchrow(query, text_id)
        return dict(row) if row else None


async def update_text(pool, text_id: int, updated_text) -> Optional[dict]:
    async with pool.acquire() as connection:
        query = """
        UPDATE texts 
        SET text = $1, topic = $2, difficult = $3 
        WHERE id = $4 RETURNING id, text, topic, difficult;
        """
        row = await connection.fetchrow(query, updated_text.text, updated_text.topic, updated_text.difficult, text_id)
        return dict(row) if row else None


async def delete_text(pool, text_id: int) -> None:
    async with pool.acquire() as connection:
        query = "DELETE FROM texts WHERE id = $1;"
        await connection.execute(query, text_id)