from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.base import AbstractModel
import asyncio
from aiogram import Bot, Dispatcher
from handlers import registration, main_func, work
from middlewares.db import DbSessionMiddleware
import os
from dotenv import load_dotenv


load_dotenv()


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
token = os.getenv("API_TOKEN")
db_pass = os.getenv("DB_PASS")

async def main():
    engine = create_async_engine(url='postgresql+psycopg://postgres:{db_pass}\@localhost/python'.format(db_pass=db_pass), echo=True)
    async with engine.begin() as conn:
        # await conn.run_sync(AbstractModel.metadata.drop_all)

        await conn.run_sync(AbstractModel.metadata.create_all)
    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_routers(registration.router, main_func.router, work.router)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

