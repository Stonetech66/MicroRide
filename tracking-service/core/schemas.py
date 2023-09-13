from pydantic import BaseModel, Field


class Location(BaseModel):
    lon: float = Field(le=180, ge=-180)
    lat: float=Field(le=90, ge=-90)