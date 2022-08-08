

from . import models, schemas
from fastapi import HTTPException, status
from ..security.hashing import Hash
from bson import ObjectId


def create(request: schemas.User, db):
    new_user = schemas.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password))

    if hasattr(new_user, 'id'):
        delattr(new_user, 'id')

    db.users.insert_one(new_user.dict(by_alias=True))

    return new_user


def show(id: str, db):
    return schemas.User(**db.users.find_one({'_id': ObjectId(id)}))
