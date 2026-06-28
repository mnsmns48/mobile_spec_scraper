from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_basic.schemas import TypeAndBrandResponse, TypeModel, BrandModel
from database.models import Brand, Product_Type, Product


async def get_existing_brand(session: AsyncSession, brand_name: str) -> Brand | None:
    result = await session.execute(select(Brand).where(Brand.brand == brand_name))
    return result.scalar_one_or_none()


async def get_existing_type(session: AsyncSession, type_name: str) -> Product_Type | None:
    result = await session.execute(select(Product_Type).where(Product_Type.type == type_name))
    return result.scalar_one_or_none()


async def update_existing_brand(session: AsyncSession, brand: Brand, new_words: list[str]) -> Brand:
    current = set(brand.brand_depends)
    updated = list(current.union(new_words))

    brand.brand_depends = updated
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand


async def create_new_brand(session: AsyncSession, brand_name: str, kind_list: list[str]) -> Brand:
    new_brand = Brand(brand=brand_name, brand_depends=kind_list)
    session.add(new_brand)
    await session.commit()
    await session.refresh(new_brand)
    return new_brand


async def update_existing_type(session: AsyncSession, type_obj: Product_Type, new_words: list[str]) -> Product_Type:
    current = set(type_obj.kind)
    updated = list(current.union(new_words))

    type_obj.kind = updated
    session.add(type_obj)
    await session.commit()
    await session.refresh(type_obj)
    return type_obj


async def create_new_type(session: AsyncSession, type_name: str, kind_list: list[str]) -> Product_Type:
    new_type = Product_Type(type=type_name, kind=kind_list)
    session.add(new_type)
    await session.commit()
    await session.refresh(new_type)
    return new_type


async def get_type_and_brand(brand_name: str, type_name: str, session: AsyncSession) -> TypeAndBrandResponse:
    brand_name = brand_name.lower().strip()
    type_name = type_name.lower().strip()

    type_result = await session.execute(select(Product_Type).where(Product_Type.type == type_name))
    type_obj = type_result.scalar_one_or_none()

    if not type_obj:
        raise HTTPException(status_code=404, detail=f"Тип '{type_name}' не найден")

    brand_result = await session.execute(select(Brand).where(Brand.brand == brand_name))
    brand_obj = brand_result.scalar_one_or_none()

    if not brand_obj:
        raise HTTPException(status_code=404, detail=f"Бренд '{brand_name}' не найден")

    return TypeAndBrandResponse(type=TypeModel(type_id=type_obj.id, type_title=type_obj.type),
                                brand=BrandModel(brand_id=brand_obj.id, brand_title=brand_obj.brand))


async def get_feature_and_validate_pros_cons(product_title: str, attribute: str, session: AsyncSession) -> Product:
    result = await session.execute(select(Product).where(Product.title_line == product_title.strip()))
    feature = result.scalar_one_or_none()

    if not feature:
        raise HTTPException(status_code=404, detail=f"Product with title '{product_title}' not found")

    if not feature.pros_cons:
        feature.pros_cons = {"advantage": [], "disadvantage": []}

    if attribute not in feature.pros_cons:
        raise HTTPException(status_code=400, detail=f"Attribute '{attribute}' not found in pros_cons")

    return feature


async def get_feature(product_title: str, session: AsyncSession) -> Product | None:
    result = await session.execute(select(Product).where(Product.title_line == product_title.strip()))
    feature = result.scalar_one_or_none()
    return feature or None


async def save_feature(session: AsyncSession, feature: Product):
    await session.commit()
    await session.refresh(feature)
    return feature.info
