import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import AsyncSessionLocal
from models import Product


SAMPLE_PRODUCTS = [
    {
        "name": "T-Shirt Basique Blanc",
        "description": "Le classique intemporel. 100% coton bio, coupe droite confortable, idéal pour toutes les occasions.",
        "price": 27.0,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Blanc", "Écru"],
        "stock": 150,
    },
    {
        "name": "T-Shirt Premium Noir",
        "description": "Qualité supérieure, coton peigné 220g/m². Coupe ajustée moderne, résistant au lavage.",
        "price": 32.0,
        "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Noir", "Marine"],
        "stock": 120,
    },
    {
        "name": "T-Shirt Vintage Gris",
        "description": "Look vintage authentique, effet délavé naturel. Coton recyclé, édition limitée.",
        "price": 35.0,
        "image_url": "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=600",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Gris chiné", "Beige vintage"],
        "stock": 80,
    },
]


async def seed_products(db: AsyncSession) -> None:
    result = await db.execute(select(Product).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    for data in SAMPLE_PRODUCTS:
        product = Product(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            image_url=data["image_url"],
            sizes_json=json.dumps(data["sizes"]),
            colors_json=json.dumps(data["colors"]),
            stock=data["stock"],
        )
        db.add(product)

    await db.commit()
    print(f"[seed] {len(SAMPLE_PRODUCTS)} produits insérés.")


async def run_seed() -> None:
    async with AsyncSessionLocal() as db:
        await seed_products(db)


if __name__ == "__main__":
    asyncio.run(run_seed())
