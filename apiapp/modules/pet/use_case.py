"""
Pet use case - business logic and data access
Simplified pattern using Beanie's built-in methods directly
"""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import paginate

from .model import Pet
from .schemas import CreatePet, UpdatePet, PetResponse


class PetUseCase:
    """
    Pet use case handling both business logic and data access.
    Uses Beanie Document methods directly for simplicity.
    """

    # ==================== Create Operations ====================

    async def create(self, data: CreatePet) -> PetResponse:
        """Create a new pet"""
        pet = Pet(
            **data.model_dump(),
            created_at=datetime.now(timezone.utc),
        )

        await pet.insert()
        return self._to_response(pet)

    # ==================== Read Operations ====================

    async def get_by_id(self, pet_id: str) -> Optional[PetResponse]:
        """Get pet by ID"""
        pet = await Pet.get(PydanticObjectId(pet_id))
        return self._to_response(pet) if pet else None

    async def get_list(self) -> Page[PetResponse]:
        """Get paginated list of pets"""
        find_query = Pet.find_all().sort("-created_at")
        page = await paginate(find_query)
        return self._page_to_response(page)

    # ==================== Update Operations ====================

    async def update(self, pet_id: str, data: UpdatePet) -> Optional[PetResponse]:
        """Update pet with validation"""
        pet = await Pet.get(PydanticObjectId(pet_id))
        if not pet:
            return None

        update_data = data.model_dump(exclude_none=True)

        # Update fields
        for key, value in update_data.items():
            setattr(pet, key, value)

        pet.updated_at = datetime.now(timezone.utc)
        await pet.save()

        return self._to_response(pet)

    # ==================== Delete Operations ====================

    async def delete(self, pet_id: str) -> bool:
        """Delete pet by ID"""
        pet = await Pet.get(PydanticObjectId(pet_id))
        if not pet:
            return False

        await pet.delete()
        return True

    # ==================== Private Helpers ====================

    def _to_response(self, pet: Pet) -> PetResponse:
        """Convert Pet model to PetResponse"""
        return PetResponse.model_validate(pet.model_dump())

    def _page_to_response(self, page: Page[Pet]) -> Page[PetResponse]:
        """Convert paginated Pets to paginated PetResponse"""
        return Page(
            items=[self._to_response(pet) for pet in page.items],
            total=page.total,
            page=page.page,
            size=page.size,
            pages=page.pages,
        )


# Dependency injection
def get_pet_use_case() -> PetUseCase:
    """Get PetUseCase instance"""
    return PetUseCase()
