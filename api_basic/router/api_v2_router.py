from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api_auth.dependencies.api_connect import verify_service_token
from api_basic.crud import get_existing_brand, update_existing_brand, create_new_brand, get_existing_type, \
    update_existing_type, create_new_type, get_type_and_brand
from api_basic.helpers import clean_kind_list, normalize_title_line

from api_basic.schemas import ItemInfoRequest, ProductResponse, CreateNewEntityRequest, CreateFeaturesGlobal
from api_basic.service.info import FeatureInfo, InsertBulkParams, CreateFeatureCategory, DeleteFeatureCategory, \
    UpdateFeatureCategory, InnerRowRequest, UpdateInnerRowRequest
from api_basic.service.pros_cons import ProsConsItemCreate, ProsConsProcedures, ProsConsItemUpdate, ProsConsItemDelete
from core.basic.logic_module import add_new_one
from core.basic.search_device_module import search_product_by_model, search_devices, all_dependencies
from database.engine import db
from database.models import Product, Brand, Product_Type

api_v2_router = APIRouter(tags=['Api V2 TOKEN'])


@api_v2_router.post("/get_one/")
async def get_one_item(data: str):
    async with db.scoped_session() as session:
        brand = await search_product_by_model(session=session,
                                              query_string=data, model=Brand, tsv_column=Brand.brand_depends_tsv)
        if brand:
            conditions = {'brand_id': brand.id}
        result = await search_devices(session=session, query_string=data, conditions=conditions)
    return result


@api_v2_router.post("/get_dependency_list/")
async def get_dependency_list(item: str,
                              session: AsyncSession = Depends(db.session_getter)):
    brand = await search_product_by_model(session=session,
                                          query_string=item, model=Brand, tsv_column=Brand.brand_depends_tsv)

    ptype = await search_product_by_model(session=session,
                                          query_string=item, model=Product_Type, tsv_column=Product_Type.kind_tsv)
    if brand or ptype:
        result = await all_dependencies(session=session, brand=brand, ptype=ptype)
        return result


@api_v2_router.post("/refresh_item")
async def refresh_item(payload: ItemInfoRequest, session: AsyncSession = Depends(db.session_getter)):
    stmt = (
        select(Product)
        .options(
            selectinload(Product.brand),
            selectinload(Product.product_type)
        )
        .join(Brand, Product.brand_id == Brand.id)
        .join(Product_Type, Product.product_type_id == Product_Type.id)
        .where(
            Product.title_line == payload.title,
            Brand.brand == payload.brand,
            Product_Type.type == payload.type,
        )
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        return None

    updated_result = await add_new_one(session=session, url=product.link)
    if updated_result.get("response") == 'updated':
        return ProductResponse(title_line=updated_result["title_line"],
                               source=updated_result["source"],
                               pros_cons=updated_result.get("pros_cons"),
                               info=updated_result["info"])


@api_v2_router.post("/create_new_entity/")
async def create_new_entity(payload: CreateNewEntityRequest,
                            session: AsyncSession = Depends(db.session_getter)):
    cleaned_kind = clean_kind_list(payload.kind)

    if payload.brand:
        brand_name = payload.brand.lower().strip()
        existing_brand = await get_existing_brand(session, brand_name)

        if existing_brand:
            current = set(existing_brand.brand_depends)
            new_words = [w for w in cleaned_kind if w not in current]

            if new_words:
                updated_brand = await update_existing_brand(session, existing_brand, new_words)
                return {"status": "ok",
                        "created": "brand_updated",
                        "id": updated_brand.id,
                        "brand": updated_brand.brand,
                        "kind": updated_brand.brand_depends,
                        "added_words": new_words}

            return {"status": "ok",
                    "created": "brand_exists",
                    "id": existing_brand.id,
                    "brand": existing_brand.brand,
                    "kind": existing_brand.brand_depends,
                    "added_words": []}

        new_brand = await create_new_brand(session, brand_name, cleaned_kind)
        return {"status": "ok",
                "created": "brand",
                "id": new_brand.id,
                "brand": new_brand.brand,
                "kind": new_brand.brand_depends}

    if payload.type:
        type_name = payload.type.lower().strip()
        existing_type = await get_existing_type(session, type_name)

        if existing_type:
            current = set(existing_type.kind)
            new_words = [w for w in cleaned_kind if w not in current]

            if new_words:
                updated_type = await update_existing_type(session, existing_type, new_words)
                return {"status": "ok",
                        "created": "type_updated",
                        "id": updated_type.id,
                        "type": updated_type.type,
                        "kind": updated_type.kind,
                        "added_words": new_words}

            return {"status": "ok",
                    "created": "type_exists",
                    "id": existing_type.id,
                    "type": existing_type.type,
                    "kind": existing_type.kind,
                    "added_words": []}

        new_type = await create_new_type(session, type_name, cleaned_kind)
        return {"status": "ok",
                "created": "type",
                "id": new_type.id,
                "type": new_type.type,
                "kind": new_type.kind}

    raise HTTPException(status_code=400, detail="Неверный payload")


@api_v2_router.post("/create_new_feature_global/")
async def create_new_feature_global(payload: CreateFeaturesGlobal,
                                    session: AsyncSession = Depends(db.session_getter)):
    type_brand = await get_type_and_brand(brand_name=payload.brand_obj, type_name=payload.type_obj, session=session)

    title_line = normalize_title_line(payload.title)

    parts = title_line.split()
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="title должен содержать минимум два слова")

    title = " ".join(parts[1:]).lower()

    now = datetime.utcnow()

    new_product = Product(title_line=title_line, title=title,
                          brand_id=type_brand.brand.brand_id,
                          product_type_id=type_brand.type.type_id,
                          link=datetime.utcnow().strftime("%Y-%m-%d---%H:%M:%S"),
                          source="custom",
                          info={},
                          pros_cons=None,
                          create=now,
                          update=now)

    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)

    return {"status": "ok", "id": new_product.id, "title_line": new_product.title_line,
            "title": new_product.title, "brand_id": new_product.brand_id,
            "product_type_id": new_product.product_type_id}


@api_v2_router.post("/add_pros_cons_value/")
async def add_pros_cons_value_db(payload: ProsConsItemCreate,
                                 session: AsyncSession = Depends(db.session_getter)):
    return await ProsConsProcedures.add_pros_cons_value(payload, session)


@api_v2_router.post("/update_pros_cons_value/")
async def update_pros_cons_value_db(payload: ProsConsItemUpdate,
                                    session: AsyncSession = Depends(db.session_getter)):
    return await ProsConsProcedures.update_pros_cons_value(payload, session)


@api_v2_router.post("/delete_pros_cons_value/")
async def delete_pros_cons_value_db(payload: ProsConsItemDelete,
                                    session: AsyncSession = Depends(db.session_getter)):
    return await ProsConsProcedures.delete_pros_cons_value(payload, session)


@api_v2_router.post("/insert_bulk_data_in_info/")
async def insert_bulk_data_in_info(payload: InsertBulkParams, session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.insert_bulk_data_in_info(payload, session)


@api_v2_router.post("/create_new_info_category/")
async def create_new_info_category(payload: CreateFeatureCategory, session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.create_new_info_category_db(payload, session)


@api_v2_router.post("/delete_info_category/")
async def delete_info_category_db(payload: DeleteFeatureCategory, session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.delete_info_category_db(payload, session)


@api_v2_router.post("/update_info_category/")
async def update_info_category_db(payload: UpdateFeatureCategory, session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.update_info_category_db(payload, session)


@api_v2_router.post("/add_new_features_inner_row/")
async def add_new_features_inner_row_db(payload: InnerRowRequest, session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.add_new_features_inner_row_db(payload, session)


@api_v2_router.post("/update_features_inner_row/")
async def update_features_inner_row_db(payload: UpdateInnerRowRequest,
                                       session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.update_features_inner_row_db(payload, session)


@api_v2_router.post("/delete_features_inner_row/")
async def delete_features_inner_row_db(payload: InnerRowRequest,
                                       session: AsyncSession = Depends(db.session_getter)):
    return await FeatureInfo.delete_features_inner_row_db(payload, session)
