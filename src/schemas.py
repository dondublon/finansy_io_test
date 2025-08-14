from pydantic import BaseModel, AnyHttpUrl

class LinkCreate(BaseModel):
    url: AnyHttpUrl

class LinkCreateResponse(BaseModel):
    short_key: str
    url: AnyHttpUrl
    # use_counter: int

    class Config:
        orm_mode = True

#class LinkByKey(BaseModel):
#    short_key: str

