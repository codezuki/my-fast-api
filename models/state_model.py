from typing import Optional

from pydantic import BaseModel, Field, field_validator

class StateModel(BaseModel):
    State_SK: int = 0
    StateName: Optional[str] = None
    StateCode: Optional[str] = None
    Country_SK: int = 0
    IsActive: bool = False

class StateListModel(BaseModel):
    StateList: list[StateModel] = Field(default_factory=list)

class SaveStateModel(BaseModel):
    StateName: str = Field(min_length=1, max_length=100)
    StateCode: str = Field(min_length=1, max_length=20)
    Country_SK: int = Field(gt=0)
    IsActive: bool = False
    User_SK: int = Field(default=0, ge=0)

    @field_validator("StateName", "StateCode")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

class UpdateStateModel(BaseModel):
    State_SK: int = Field(gt=0)
    StateName: str = Field(min_length=1, max_length=100)
    StateCode: str = Field(min_length=1, max_length=20)
    Country_SK: int = Field(gt=0)
    IsActive: bool = False
    User_SK: int = Field(default=0, ge=0)

    @field_validator("StateName", "StateCode")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

class DeleteStateModel(BaseModel):
    State_SK: int = Field(gt=0)
    User_SK: int = Field(default=0, ge=0)

class GetCountriesDrpModel(BaseModel):
    Country_SK: int = 0
    CountryName: Optional[str] = None
   # CountryCode: Optional[str] = None    

class GetCountryStateModel(BaseModel):
    Country_SK: int = 0
    StateList: list[StateModel] = Field(default_factory=list)
