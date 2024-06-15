from fastapi import APIRouter

router = APIRouter()

@router.post('/', tags=["users"]
 async def read_users():
   return [{"username": "Rick"}, {"username": "Morty"}])