from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    avatar: str | None
    language: str
    timezone: str
    is_active: bool
    is_verified: bool


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=20, max_length=200)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserRoleUpdate(BaseModel):
    role_name: str = Field(..., min_length=2, max_length=50)


class UserSelfUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=3, max_length=200)
    avatar: str | None = Field(default=None, max_length=500)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    timezone: str | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "UserSelfUpdate":
        if not self.model_fields_set:
            raise ValueError("Indique pelo menos um campo para atualizar")
        nullable_fields = self.model_fields_set - {"avatar"}
        if any(getattr(self, field) is None for field in nullable_fields):
            raise ValueError("Nome, idioma e fuso horário não podem ser nulos")
        return self


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    avatar: str | None
    language: str
    timezone: str
    is_active: bool
    is_verified: bool
    role: RoleResponse | None = None
    permissions: list[str] = []
