from datetime import datetime
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from api_basic.crud import get_feature_and_validate_pros_cons


class ProsConsItemCreate(BaseModel):
    product_title: str
    attribute: Literal["advantage", "disadvantage"]
    value: str


class ProsConsItemUpdate(ProsConsItemCreate):
    new_value: str


class ProsConsItemDelete(ProsConsItemCreate):
    pass


class ProsConsProcedures:
    @staticmethod
    async def add_pros_cons_value(payload: ProsConsItemCreate, session: AsyncSession):
        feature = await get_feature_and_validate_pros_cons(product_title=payload.product_title,
                                                           attribute=payload.attribute,
                                                           session=session)
        if feature:
            items = feature.pros_cons[payload.attribute]
            updated_items = items + [payload.value]

            feature.pros_cons = {**feature.pros_cons, payload.attribute: updated_items}

            feature.update = datetime.utcnow()

            await session.commit()
            await session.refresh(feature)

            return {"status": "ok", "product_id": feature.id, "attribute": payload.attribute,
                    "value": payload.value, "pros_cons": feature.pros_cons}

    @staticmethod
    async def update_pros_cons_value(payload: ProsConsItemUpdate, session: AsyncSession):
        feature = await get_feature_and_validate_pros_cons(product_title=payload.product_title,
                                                           attribute=payload.attribute,
                                                           session=session)
        if feature:
            items = feature.pros_cons[payload.attribute]
            if payload.value not in items:
                raise HTTPException(status_code=404,
                                    detail=f"Value '{payload.value}' not found in '{payload.attribute}' list")

            updated_items = [payload.new_value if item == payload.value else item for item in items]

            feature.pros_cons = {**feature.pros_cons, payload.attribute: updated_items}
            feature.update = datetime.utcnow()
            await session.commit()
            await session.refresh(feature)

            return {"status": "ok",
                    "product_id": feature.id,
                    "attribute": payload.attribute,
                    "old_value": payload.value,
                    "new_value": payload.new_value,
                    "pros_cons": feature.pros_cons}

    @staticmethod
    async def delete_pros_cons_value(payload: ProsConsItemDelete, session: AsyncSession):
        feature = await get_feature_and_validate_pros_cons(product_title=payload.product_title,
                                                           attribute=payload.attribute,
                                                           session=session)
        if feature:
            items = feature.pros_cons[payload.attribute]

            if payload.value not in items:
                raise HTTPException(status_code=404,
                                    detail=f"Value '{payload.value}' not found in '{payload.attribute}' list")
            updated_items = [item for item in items if item != payload.value]
            feature.pros_cons = {**feature.pros_cons, payload.attribute: updated_items}
            feature.update = datetime.utcnow()

            await session.commit()
            await session.refresh(feature)

            return {"status": "ok",
                    "product_id": feature.id,
                    "attribute": payload.attribute,
                    "deleted_value": payload.value,
                    "pros_cons": feature.pros_cons}
