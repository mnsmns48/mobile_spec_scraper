from typing import List

from pydantic import BaseModel, model_validator


class ItemList(BaseModel):
    items: List[str]


class ItemInfoRequest(BaseModel):
    title: str
    brand: str | None = None
    type: str | None = None


class ProductResponse(BaseModel):
    title_line: str
    source: str
    pros_cons: dict | None = None
    info: list

    class Config:
        from_attributes = True


class CreateNewEntityRequest(BaseModel):
    type: str | None = None
    brand: str | None = None
    kind: list[str] | None = None

    @model_validator(mode="after")
    def validate_pairs(self):

        if not self.kind:
            raise ValueError("Поле 'kind' обязательно")

        if self.type and self.brand:
            raise ValueError("Нельзя передавать одновременно 'type' и 'brand'")

        if self.type and self.kind:
            return self

        if self.brand and self.kind:
            return self

        raise ValueError("Должны быть переданы либо (type и kind), либо (brand и kind)")


class TypeModel(BaseModel):
    type_id: int
    type_title: str


class BrandModel(BaseModel):
    brand_id: int
    brand_title: str


class TypeAndBrandResponse(BaseModel):
    type: TypeModel
    brand: BrandModel


class CreateFeaturesGlobal(BaseModel):
    title: str
    type_obj: str
    brand_obj: str
