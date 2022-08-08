from fastapi import APIRouter
from ..repository import database, schemas, models, user
from fastapi import APIRouter, Depends, status
from ..repository.schemas import ResponseModel, ErrorResponseModel
from ..security import oauth2

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

get_db = database.get_db


@router.post('/', response_model=schemas.User)
def create_user(request: schemas.User, db=Depends(get_db)):
    return user.create(request, db)

@router.get('/my/profile')
def all(db=Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    print(current_user)
    return ResponseModel(current_user, "User data retrieved successfully")

@router.get('/{id}')
def get_user(id: str, db=Depends(get_db)):
    user_ = user.show(id, db)

    if hasattr(user_, 'password'):
        delattr(user_, 'password')

    if user_:
        return ResponseModel(user_, "User data retrieved successfully")

    return ErrorResponseModel(user_, "User not found")


@router.get('/')
async def list_users(db=Depends(get_db)):
    users = []

    for user in db.users.find():
        if hasattr(user, 'password'):
            delattr(user, 'password')

        users.append(schemas.User(**user))

    return ResponseModel(users, "User data retrieved successfully")


