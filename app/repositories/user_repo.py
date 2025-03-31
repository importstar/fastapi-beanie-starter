from bson import ObjectId
from beanie import Document

from app import models, schemas
from app.repositories.base_repo import BaseRepository
from app.core.exceptions import ValidationError

from loguru import logger


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(models.User)

    async def get_unique_username(self, username: str) -> Document | None:
        try:
            item = self.model.objects(username=username).first()
        except Exception:
            raise ValidationError(detail="Invalid username")

        return item
