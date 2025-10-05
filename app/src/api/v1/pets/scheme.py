from pydantic import BaseModel

class PetsRequest(BaseModel):
    pass

class PetsResponse(BaseModel):
    name: str
    age: int
    location: str
    image : list[bytes]