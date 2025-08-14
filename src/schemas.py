from urllib.parse import urlparse
from pydantic import BaseModel, AnyHttpUrl, field_validator


class LinkCreate(BaseModel):
    url: str

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL")
        return v

class LinkCreateResponse(BaseModel):
    short_key: str
    url: AnyHttpUrl
    # use_counter: int

    class Config:
        orm_mode = True

#class LinkByKey(BaseModel):
#    short_key: str

