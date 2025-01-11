from fastapi import APIRouter, Depends


from app.auth.utils import get_access_token
from app.ideas.schemas import IdeaResponse

from app.repositories.idea_repository import IdeaRepository
from app.repositories.idea_repository import get_idea_repository

idea_router = APIRouter(prefix="/ideas", tags=["Ideas"])


@idea_router.post("/add_idea")
async def add_idea(idea: IdeaResponse, session: IdeaRepository = Depends(get_idea_repository),
                   access_data: dict | bool = Depends(get_access_token)):
    return await session.add_idea(idea, access_data)


@idea_router.get("/all_ideas")
async def get_all_ideas(session: IdeaRepository = Depends(get_idea_repository), access_data: dict | bool = Depends(get_access_token)):
    return await session.get_ideas(access_data)


@idea_router.get("/delete_all")
async def delete_all(session: IdeaRepository = Depends(get_idea_repository),access_data: dict | bool = Depends(get_access_token)):
    return await session.drop_all_ideas(access_data)

@idea_router.patch("/update_idea")
async def patch_idea(idea: IdeaResponse, access_data: dict | bool = Depends(get_access_token), session: IdeaRepository = Depends(get_idea_repository)):
    return await session.update_idea(idea, access_data)


@idea_router.delete("/delete_idea/{title}")
async def delete_idea(title: str, access_data: dict | bool = Depends(get_access_token), session: IdeaRepository = Depends(get_idea_repository)):
    return await session.delete_idea(title, access_data)

@idea_router.get("/get_ideas_by_description/{description}")
async def get_ideas(description: str, session: IdeaRepository = Depends(get_idea_repository), access_data: dict | bool = Depends(get_access_token)):
    return await session.search_for_idea_by_description(description, access_data)

@idea_router.get("/get_user_ideas")
async def get_ideas(session: IdeaRepository = Depends(get_idea_repository), access_data: dict | bool = Depends(get_access_token)):
    return await session.get_ideas_by_id(access_data)