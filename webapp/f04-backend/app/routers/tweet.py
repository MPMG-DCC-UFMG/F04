from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from ..repository import schemas, database, models
from ..security import oauth2
from ..repository import tweet
from ..repository.schemas import ResponseModel, ErrorResponseModel
from datetime import datetime
from bson import ObjectId

router = APIRouter(
    prefix="/tweets",
    tags=['Tweets']
)

get_db = database.get_db


@router.get('/')
def all(db=Depends(get_db),
        current_user: schemas.User = Depends(oauth2.get_current_user),
        top_n: Optional[int] = 10,
        q: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        retweets: Optional[str] = 'up',
        hashtags: Optional[str] = None,
        user: Optional[str] = None,
        political: Optional[str] = None,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortby: Optional[str] = 'created_at'):

    tweets, total = tweet.get_all(db,
                                  top_n=top_n,
                                  start_date=start_date,
                                  end_date=end_date,
                                  q=q,
                                  retweets=retweets,
                                  user=user,
                                  political=political,
                                  sortby=sortby,
                                  page=page,
                                  hashtags=hashtags,
                                  per_page=per_page)

    if tweets:
        return ResponseModel(tweets, "Tweets data retrieved successfully", total=total)

    return ResponseModel(tweets, "Empty list returned")


@router.post('/', status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create(request: schemas.Tweet, db=Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ErrorResponseModel('An error occurred', 501, 'Not implemented yet!')


@router.delete('/{id}', status_code=status.HTTP_501_NOT_IMPLEMENTED)
def destroy(id: str, db=Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ErrorResponseModel('An error occurred', 501, 'Not implemented yet!')


@router.put('/{id}', status_code=status.HTTP_501_NOT_IMPLEMENTED)
def update(id: str, request: schemas.Tweet, db=Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ErrorResponseModel('An error occurred', 501, 'Not implemented yet!')


@router.get('/{id}', status_code=200)
async def show(id: str, db=Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    print("show", id)
    tweet_ = tweet.show(id, db)

    if tweet_:
        return ResponseModel(tweet_, "Tweet data retrieved successfully")

    return ResponseModel(tweet_, "Tweet not found")


@router.get('/hashtags/stats', status_code=200)
async def top_n_hashtags(db=Depends(get_db),
                         current_user: schemas.User = Depends(
        oauth2.get_current_user),
        top_n: Optional[int] = 10,
        is_retweet: Optional[bool] = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None):

    agg = tweet.top_n_hashtags(
        db, top_n, is_retweet, start_date=start_date, end_date=end_date)

    return ResponseModel(agg, "Stats computed successfully")


@router.get('/links/stats', status_code=200)
async def top_n_links(db=Depends(get_db),
                      current_user: schemas.User = Depends(
        oauth2.get_current_user),
        top_n: Optional[int] = 10,
        is_retweet: Optional[bool] = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None):

    agg = tweet.top_n_links(db, top_n, is_retweet,
                            start_date=start_date, end_date=end_date)

    return ResponseModel(agg, "Stats computed successfully")


@router.get('/users/stats', status_code=200)
async def top_n_users(db=Depends(get_db),
                      current_user: schemas.User = Depends(
        oauth2.get_current_user),
        top_n: Optional[int] = 10,
        is_retweet: Optional[bool] = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None):

    agg = tweet.top_n_users(db, top_n, is_retweet,
                            start_date=start_date, end_date=end_date)

    return ResponseModel(agg, "Stats computed successfully")

@router.get('/labeling/{tweet_id}/{label}', status_code=200)
async def labeling(tweet_id, label, db=Depends(get_db), current_user: schemas.User = Depends( oauth2.get_current_user)):

    if label:
        db.tweets.find_one_and_update({'_id': ObjectId(tweet_id)}, {"$set": {"political": str(label)}})
        db.tweets.find_one_and_update({'_id': tweet_id}, {"$set": {"political": str(label)}})
    else:
        db.tweets.find_one_and_update({'_id': ObjectId(tweet_id)}, {"$unset": {"political": None}})
        db.tweets.find_one_and_update({'_id': tweet_id}, {"$unset": {"political": None}})
    
    tweet = db.tweets.find_one ({'_id': ObjectId(tweet_id)})

    if (tweet == None):
        tweet = db.tweets.find_one ({'_id': tweet_id})

    return schemas.Tweet(**tweet) 
