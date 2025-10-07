from pydantic import BaseModel

class OrigPhoto(BaseModel):
    height: int
    type: str
    url: str
    width: int

class Photo(BaseModel):
    id: int
    date: int
    access_key: str
    orig_photo: OrigPhoto

class Attachments(BaseModel):
    type: str
    photo:Photo

class PetsResponse(BaseModel):
    id: int
    attachments: list[Attachments]
    new_token: int
    description: str

class PetsRequest(BaseModel):
    user_id: int
    next_token: int  

