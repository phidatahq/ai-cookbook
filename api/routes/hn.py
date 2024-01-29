from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from hn_ai.knowledge import load_hackernews_knowledge_base

######################################################
## Router for Hackernews Assistant
######################################################

hn_router = APIRouter(prefix=endpoints.HN, tags=["HackerNews"])


class LoadKnowledgeBaseRequest(BaseModel):
    key: Optional[str] = None


@hn_router.post("/load-knowledge-base")
def load_knowledge_base(body: LoadKnowledgeBaseRequest):
    """Loads the hackernews knowledge base"""

    status = load_hackernews_knowledge_base()
    return {"message": status}
