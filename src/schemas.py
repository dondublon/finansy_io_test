from pydantic import BaseModel, AnyHttpUrl


class LinkCreate(BaseModel):
    url: str


class LinkCreateResponse(BaseModel):
    short_key: str
    url: AnyHttpUrl

    class Config:
        orm_mode = True
