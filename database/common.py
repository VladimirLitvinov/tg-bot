from sqlalchemy import select

from database.base import async_session
from database.models import History


async def add_new_history(user_params: dict) -> None:
    """
    Adds the user's request to the database
    :param user_params: User's request dict '
    :return: None
    """
    async with async_session() as session:
        new_history = History(**user_params)
        session.add(new_history)
        await session.commit()


async def get_history(user_tg_id: int) -> list[History]:
    """
    Get user history
    :param user_tg_id: User's telegram id '
    :return: List of history objects in database
    """
    async with async_session() as session:
        history = await session.execute(
            select(History)
            .filter(History.user_tg_id == user_tg_id)
            .order_by(History.date_search)
            .limit(10))
        result = history.scalars().all()
        return result
