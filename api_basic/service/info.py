import logging
from typing import List, Dict

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from api_basic.crud import get_feature, save_feature
from api_basic.helpers import find_category_index, normalize_title_line
from config import logger


class InsertedBlock(BaseModel):
    param: str
    bulk: str


class InsertBulkParams(BaseModel):
    feature_title: str
    bulk: List[InsertedBlock]


class FeatureResponseScheme(BaseModel):
    id: int
    title: str
    info: List[Dict]
    pros_cons: dict | None = None


class CreateFeatureCategory(BaseModel):
    feature_title: str
    category: str


class DeleteFeatureCategory(CreateFeatureCategory):
    pass


class UpdateFeatureCategory(CreateFeatureCategory):
    new_category: str


class InnerRowRequest(BaseModel):
    feature_title: str
    category_title: str
    new_param: str
    new_value: str


class UpdateInnerRowRequest(InnerRowRequest):
    old_param: str
    old_value: str


class FeatureInfo:
    @staticmethod
    async def insert_bulk_data_in_info(payload: InsertBulkParams, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []

            if not isinstance(info, list):
                raise HTTPException(status_code=500, detail="Поле info должно быть списком.")

            info = list(info)

            for block in payload.bulk:
                block_name = block.param.strip()
                block_text = block.bulk.strip()

                if not block_name:
                    raise HTTPException(status_code=400, detail="Поле 'param' не может быть пустым.")

                parsed = dict()

                for line in block_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    if ":" not in line:
                        raise HTTPException(status_code=400,
                                            detail=f"Неверный формат строки: '{line}'. Ожидается 'параметр: значение'.")

                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if not key or not value:
                        raise HTTPException(status_code=400, detail=f"Неверный формат строки: '{line}'.")

                    parsed[key] = value

                info.append({block_name: parsed})

            feature.info = info
            flag_modified(feature, "info")
            await session.commit()
            await session.refresh(feature)
            return FeatureResponseScheme(id=feature.id, title=feature.title, info=list(feature.info or []),
                                         pros_cons=feature.pros_cons or {})

    @staticmethod
    async def create_new_info_category_db(payload: CreateFeatureCategory, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []
            index = find_category_index(info, payload.category)
            if index is not None:
                return {"status": "exists", "info": info}

            info.append({payload.category: {}})
            feature.info = info

            updated_info = await save_feature(session, feature)
            return {"status": "created", "info": updated_info}

    @staticmethod
    async def delete_info_category_db(payload: DeleteFeatureCategory, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []
            index = find_category_index(info, payload.category)
            if index is None:
                raise HTTPException(status_code=404, detail="Category not found")

            del info[index]
            feature.info = info
            flag_modified(feature, "info")

            await session.commit()
            await session.refresh(feature)

            return {"status": "deleted", "info": feature.info}

    @staticmethod
    async def update_info_category_db(payload: UpdateFeatureCategory, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []
            index = find_category_index(info, payload.category)
            if index is None:
                raise HTTPException(status_code=404, detail="Category not found")
            existing_index = find_category_index(info, payload.new_category)
            if existing_index is not None:
                raise HTTPException(status_code=400, detail="New category title already exists")
            old_block = info[index]
            old_values = old_block[payload.category]
            new_block = {payload.new_category: old_values}
            info[index] = new_block
            feature.info = info
            flag_modified(feature, "info")
            await session.commit()
            await session.refresh(feature)
            return {"status": "updated", "info": feature.info}

    @staticmethod
    async def add_new_features_inner_row_db(payload: InnerRowRequest, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []
            category_block = None
            for block in info:
                if payload.category_title in block:
                    category_block = block
                    break
            if not category_block:
                return {"status": "error", "message": "Category not found"}
            category_block[payload.category_title][payload.new_param] = payload.new_value

            flag_modified(feature, "info")
            await session.commit()
            await session.refresh(feature)
            return {"status": "created", "info": feature.info}

    @staticmethod
    async def update_features_inner_row_db(payload: UpdateInnerRowRequest, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            info = feature.info or []
            category_block = None
            for block in info:
                if payload.category_title in block:
                    category_block = block
                    break

            if not category_block:
                raise HTTPException(status_code=404, detail="Category not found")

            category_data = category_block[payload.category_title]

            if payload.old_param not in category_data:
                raise HTTPException(status_code=404, detail="Old param not found")

            del category_data[payload.old_param]
            category_data[payload.new_param] = payload.new_value
            flag_modified(feature, "info")

            await session.commit()
            await session.refresh(feature)

        return {"status": "updated", "info": feature.info}

    @staticmethod
    async def delete_features_inner_row_db(payload: InnerRowRequest, session: AsyncSession):
        feature = await get_feature(product_title=payload.feature_title, session=session)
        if feature:
            category_block = None
            for block in feature.info:
                if payload.category_title in block:
                    category_block = block
                    break

            if not category_block:
                raise HTTPException(status_code=404, detail="Category not found")

            category_data = category_block[payload.category_title]

            if payload.new_param not in category_data:
                raise HTTPException(status_code=404, detail="Param not found")

            del category_data[payload.new_param]

            flag_modified(feature, "info")

            await session.commit()
            await session.refresh(feature)

            return {"status": "deleted", "info": feature.info}
