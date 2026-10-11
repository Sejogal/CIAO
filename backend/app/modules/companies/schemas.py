from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class CompanyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    owner_id: UUID


class CompanyMemberCreate(BaseModel):
    user_id: UUID

    role: str = Field(
        default="member",
        max_length=50,
    )


class CompanyMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    user_id: UUID
    role: str


class CompanyMemberUpdate(BaseModel):
    role: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )


class CompanyMemberUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str


class CompanyMemberDetailedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    user_id: UUID
    role: str
    user: CompanyMemberUserResponse