from abc import ABC
from datetime import datetime

import pytz
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.auth.utils import get_access_token
from app.database.config import get_async_session
from app.database.models import Idea, User
from app.ideas.schemas import IdeaResponse


async def get_idea_repository(session: AsyncSession = Depends(get_async_session)):
    return IdeaRepository(session)


class AbstractIdeaRepository(ABC):
    async def add_idea(self, idea: IdeaResponse):
        raise NotImplementedError

    async def get_ideas(self, user_id: str = Depends(get_access_token)):
        raise NotImplementedError

    async def drop_all_ideas(self, user_id: str = Depends()):
        raise NotImplementedError

    async def update_idea(self, idea: IdeaResponse, access_data: dict | bool = Depends(get_access_token)):
        raise NotImplementedError

    async def delete_idea(self, title: str, access_data: dict | bool = Depends(get_access_token)):
        raise NotImplementedError

    async def search_for_idea_by_description(self, description: str):
        raise NotImplementedError


class IdeaRepository(AbstractIdeaRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_idea(self, idea: IdeaResponse, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Update your access token")
        idea_in_db = await self.session.execute(select(Idea).filter(Idea.title == idea.title))
        idea_in_db = idea_in_db.scalar_one_or_none()
        if idea_in_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Such idea already exists"
            )
        idea.user_id = access_data["user_id"]
        created_at = datetime.now(tz=pytz.timezone("Europe/Moscow"))
        idea.created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        idea.nickname = access_data["nickname"]
        try:
            to_add = Idea(**idea.model_dump())
            self.session.add(to_add)
            await self.session.commit()
            await self.session.refresh(to_add)
        except Exception as e:
            await self.session.rollback()
            return JSONResponse(content=f"something went wrong, details: {e.__str__()}",
                                status_code=status.HTTP_400_BAD_REQUEST)
        return {"info": f"{access_data['nickname']} has just created the idea with title {idea.title}",
                "description": idea.description}

    async def get_ideas(self, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Refresh your access token")
        query = await self.session.execute(select(User).where(User.id == access_data["user_id"]))
        query = query.scalar_one_or_none()
        if query.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough rights"
            )
        try:
            data = await self.session.execute(select(Idea))
            data = data.scalars().all()
            return data
        except Exception as e:
            return {"Error occurred during fetching data": e}

    async def drop_all_ideas(self, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Refresh your access token")
        query = await self.session.execute(select(User).where(User.id == access_data["user_id"]))
        query = query.scalar_one_or_none()
        if query.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough rights"
            )
        # only for admins!!
        try:
            await self.session.execute(text(f"ALTER SEQUENCE ideas_idea_id_seq RESTART WITH 1;"))
            await self.session.execute(delete(Idea))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            return {"Error occurred during deleting all ideas": e.__str__()}
        return JSONResponse(status_code=status.HTTP_200_OK, content="successfully deleted all ideas")

    async def update_idea(self, idea: IdeaResponse, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh your access token")
        query = await self.session.execute(
            select(Idea).filter(Idea.user_id == access_data["user_id"], Idea.title == idea.title))
        query = query.scalar_one_or_none()
        if not query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such idea doesn't exist")
        query.title = idea.title
        query.description = idea.description
        query.updated_at = datetime.now(tz=pytz.UTC)
        try:
            await self.session.commit()
            return f"{access_data['nickname']} has just updated the idea with title {idea.title}"
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={e.__name__: e.__str__()})

    async def delete_idea(self, title: str, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh your access token")
        query = await self.session.execute(
            select(Idea).filter(Idea.user_id == access_data["user_id"], Idea.title == title))
        query = query.scalar_one_or_none()
        if not query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have such idea")
        try:
            await self.session.delete(query)
            await self.session.commit()
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=f"{access_data['nickname']} has just deleted the idea: {title}")
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUESTM, detail=e.__str__())

    async def search_for_idea_by_description(self, description: str,
                                             access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Log in to search for ideas"
                                )
        user = await self.session.execute(select(User).filter(User.id == access_data["user_id"]))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User doesn't exist")
        query = await self.session.execute(
            select(Idea).filter(Idea.description.like(f"%{description}%")))
        query = query.scalars().all()
        if not query:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nothing has been found")
        return query

    async def get_ideas_by_id(self, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Log in to search for ideas"
                                )
        user = await self.session.execute(select(User).filter(User.id == access_data["user_id"]))
        user = user.scalar_one_or_none()

        ideas = await self.session.execute(select(Idea).filter(Idea.user_id == access_data["user_id"]))
        ideas = ideas.scalars().all()
        if not ideas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no ideas")
        return {"ideas": ideas, "nickname": jsonable_encoder(user.nickname)}
