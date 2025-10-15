from __future__ import annotations

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class OrganizationOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
