import os
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


async def write_answer(pool, answer: Answer) -> int:
    async with pool.acquire() as connection:
            query = """
            INSERT INTO answer (user_id, text_id, difficult, interest)
            VALUES ($1, $2, $3, $4)
            RETURNING answer_id;
            """
            answer_id = await connection.fetchval(query, 
                                                  answer.user_id, 
                                                  answer.text_id, 
                                                  answer.difficult, 
                                                  answer.interest)

            return answer_id
    