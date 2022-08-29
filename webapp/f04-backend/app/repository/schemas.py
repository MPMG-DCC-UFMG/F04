from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

import random
class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    name: str
    email: str
    password: str
    ws02token: dict

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class Login(BaseModel):
    email: str
    password: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class Tweet(BaseModel):
    id_db: Optional[PyObjectId] = Field(alias='_id')
    id: str
    text: str
    attachments: Optional[Dict] = None
    conversation_id: Optional[str] = None
    author_id: Optional[str] = None
    possibly_sensitive: Optional[bool] = None
    created_at: Optional[datetime] = None
    reply_settings:  Optional[str] = None
    lang: Optional[str] = None
    source: Optional[str] = None
    discovered_by_keyword: Optional[str] = None
    quote_count: Optional[int]
    reply_count: Optional[int]
    retweet_count: Optional[int]
    favorite_count: Optional[int]
    user: Optional[Dict] = None
    entities: Optional[Dict] = None
    referenced_tweets: Optional[List] = None
    context_annotations: Optional[List] = None
    media: Optional[List] = None
    political: Optional[str] = None
    score: Optional[float] = -1
    retweet_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class Domain(BaseModel):
    desinformacao_label: bool
    subdomain: str
    domain: str
    subdomain_ip: Optional[str] = None
    subdomain_ip_cc: Optional[str] = None
    subdomain_ip_is_brazil: Optional[bool] = None
    subdomain_ip_is_us: Optional[bool] = None
    subdomain_ip_latitude: Optional[float] = None
    subdomain_ip_longitude: Optional[float] = None
    subdomain_as_n: Optional[str] = None
    subdomain_as_cc: Optional[str] = None
    subdomain_ipcc_equal_ascc: Optional[bool] = None
    domain_route_hops: Optional[str] = None
    domain_dns_caa_txt_count: Optional[int] = None
    subdomain_has_hifen: Optional[bool] = None
    subdomain_has_numbers: Optional[bool] = None
    subdomain_tld_com_or_br: Optional[bool] = None
    subdomain_character_count: Optional[str] = None
    subdomain_has_news_keyword: Optional[bool] = None
    domain_has_whois_privacy: Optional[bool] = None
    domain_registrar_or_owner: Optional[str] = None
    domain_registrar_url: Optional[str] = None
    domain_update_date: Optional[str] = None
    domain_creation_date: Optional[str] = None
    domain_expiry_date: Optional[str] = None
    domain_days_since_creation: Optional[float] = None
    domain_days_until_expiry: Optional[float] = None
    domain_days_since_last_update: Optional[float] = None
    certificate_server_allows_insecure_requests: Optional[bool] = None
    certificate_server_redirects_insecure_requests: Optional[bool] = None
    certificate_server_public_key_bits: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_issuer_c: Optional[str] = None
    certificate_issuer_not_lets_encrypt: Optional[bool] = None
    certificate_creation_date: Optional[str] = None
    certificate_expiry_date: Optional[str] = None
    certificate_days_since_creation: Optional[str] = None
    certificate_days_until_expiry: Optional[str] = None
    certificate_lifetime: Optional[str] = None
    certificate_has_expired: Optional[bool] = None
    preview: Optional[Dict] = None
    offline: Optional[bool] = None


def ResponseModel(data, message, total=0):
    return {
        "data": data,
        "code": 200,
        "message": message,
        "total": total
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
