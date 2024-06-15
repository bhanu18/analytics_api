from fastapi import APIRouter

router = APIRouter()

@router.post('/', tags=["email"]
 async def send_mail():
   return [{"username": "Rick"}, {"username": "Morty"}])