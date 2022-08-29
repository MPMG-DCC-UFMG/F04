from . import models, schemas
from fastapi import HTTPException, status
from bson import ObjectId
import datetime
import time
import re
import random
def get_all(db, top_n, start_date, end_date, q, retweets,hashtags, user, political, sortby, page, per_page):
    tweets = []

    query = {}
    
    if q:
        query['$text'] = {'$search': q}
    if start_date:
        print(start_date.isoformat())
        query['created_at'] = {}
        query['created_at']['$gte'] = start_date.isoformat()

    if end_date:
        if 'created_at' not in query:
            query['created_at'] = {}

        query['created_at']['$lte'] = end_date.isoformat()
    if user:
        pattern = re.compile('^'+user.replace('@', '') + '$', re.I)
        query['user.username'] = {'$regex':pattern}

    if hashtags:
        pattern = re.compile('^'+hashtags.replace(',', '$|^') + '$', re.I)
        query['entities.hashtags.tag'] = {'$regex':pattern}
    #query['referenced_tweets'] = {'$exists': is_retweet}

    if political == None:
        query['political'] = { '$exists': False }
    else:
        query['political'] = { '$eq': political }
    
    sort = {}

    #if sortby == 'created_at':
    sort = [['created_at', -1]]

    
    # elif sortby == 'comments':
    #     sort = [['public_metrics.reply_count', -1]]

    #sort = [['retweet_count', -1 if retweets == 'up' else 1 ]]
    sort = [['score', -1 ], ['retweet_id', -1 if retweets == 'up' else 1 ]]
    skips = top_n * (page - 1)
  

    for tweet in db.tweets.find(query).sort(sort).skip(skips).limit(top_n):
        # TODO: simulando a atribuição de score para o tweet (mudar)
        # if 'score' not in tweet:
        #     db.tweets.find_one_and_update({'_id': tweet['_id']}, {"$set": {"score": tweet['score']}})

        tweets.append(schemas.Tweet(**tweet))

    total = db.tweets.count_documents(query)

    return tweets, total


def create(request: schemas.Tweet, db):
    pass


def destroy(id, db):
    pass


def labeling(id, request: schemas.Tweet, db):
    pass


def show(id, db):
    print('###%s###' % (id))
    return schemas.Tweet(**db.tweets.find_one({'id': id}))


def top_n_hashtags(db, top_n, is_retweet, start_date, end_date):
    aggs = db.tweets.aggregate(
        [{'$match': {
            'entities.hashtags': {'$exists': True,
                                  '$nin': []
                                  },
            # 'referenced_tweets': {'$exists': is_retweet}
        },
        },
            {'$group': {'_id': "$entities.hashtags.tag", 'total': {'$sum': 1}}},
            {'$sort': {'total': -1}},
            {'$limit': top_n}
        ])

    hashtags = {}

    for agg in aggs:
        for h in set(agg['_id']):
            if h not in hashtags:
                hashtags[h] = 0
            hashtags[h] += agg['total']

    return hashtags


def top_n_links(db, top_n, is_retweet, start_date, end_date):
    aggs = db.tweets.aggregate(
        [{'$match': {
            'entities.urls': {'$exists': True,
                              '$nin': []
                              },
           # 'referenced_tweets': {'$exists': is_retweet}
        },
        },
            {'$group': {'_id': "$entities.urls.expanded_url", 'total': {'$sum': 1}}},
            {'$sort': {'total': -1}},
            {'$limit': top_n}
        ])

    links = {}

    for agg in aggs:
        for h in set(agg['_id']):
            if h not in links:
                links[h] = 0
            links[h] += agg['total']

    return links


def top_n_users(db, top_n, is_retweet, start_date, end_date):
    aggs = db.tweets.aggregate(
        [{'$match': {
            'user.username': {'$exists': True,
                              '$nin': []
                              },
            #'referenced_tweets': {'$exists': is_retweet}
        },
        },
            {'$group': {'_id': "$user.username", 'total': {'$sum': 1}}},
            {'$sort': {'total': -1}},
            {'$limit': top_n}
        ])

    users = {}

    for agg in aggs:
        if agg['_id'] not in users:
            users[agg['_id']] = 0
        users[agg['_id']] += agg['total']

    return users
