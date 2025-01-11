
from pydantic import BaseModel



class IdeaResponse(BaseModel):
    title: str
    description: str
    user_id: str = 'dummy'
    created_at: str = 'dummy'
    nickname: str = 'dummy'

