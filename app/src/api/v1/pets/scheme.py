from pydantic import BaseModel, Field

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
    photo: Photo | None = None

class Age(BaseModel):
    years: int
    months: int
    days: int

class Contact(BaseModel):
    number: str
    name: str

class Health(BaseModel):
    status: str
    diseases: list[str] = []
    vaccinations: list[str] = []

class PetInfo(BaseModel):
    age: Age
    vaccinations: bool | None = False
    sterilization: bool | None = False
    health: Health
    temperament: list[str] = []
    contact: Contact
    name: str
    birth_place: str
    grow_up_with: str
    previous_owner: str
    owner_requirements: list[str] = []

class PetsResponse(BaseModel):
    id: int
    attachments: list[Attachments]
    next_token: int
    description: str
    pet_info: PetInfo

class PetsRequest(BaseModel):
    user_id: int
    next_token: int  

class PetsQuery(BaseModel):
    limit: int = Field(default=50)