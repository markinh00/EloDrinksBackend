import os
from dotenv import load_dotenv
from sqlmodel import Session, select, desc, distinct
from api.models.product import Product
from sqlalchemy.exc import IntegrityError
from api.schemas.pagination import ProductPagination
from api.schemas.product import ProductSearchParams, ProductUpdate
from api.services.db.cloudinary.database import Cloudinary

load_dotenv()


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, product: Product) -> Product | None:
        try:
            self.session.add(product)
            self.session.commit()
            self.session.refresh(product)
            return product
        except IntegrityError as e:
            self.session.rollback()
            return None
        except Exception as e:
            raise e

    def search(self, params: ProductSearchParams) -> list[Product]:
        for key, value in params.model_dump().items():
            if value is not None:
                statement = select(Product).where(getattr(Product, key).contains(value))
        return self.session.exec(statement).all()

    def get_all(self, query: ProductPagination) -> list[Product]:
        statement = (
            select(Product)
            .offset((query.page - 1) * query.size)
            .limit(query.size)
            .order_by(desc(query.order.value) if query.desc else query.order.value)
        )
        return list(self.session.exec(statement).all())

    def get_all_categories(self) -> list[str]:
        statement = select(distinct(Product.category))
        return list(self.session.exec(statement).all())

    def get_by_id(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    async def update(self, product_id: int, new_data: ProductUpdate) -> Product | None:
        product = self.get_by_id(product_id)

        if not product:
            return None

        cloudinary = Cloudinary()

        for key, value in new_data.model_dump().items():
            if value:
                if key == "delete_img":
                    cloudinary.delete_image(product.img_url)
                    product.img_url = os.getenv("CLOUDINARY_DEFAULT_URL")

                elif key == "img_file":
                    cloudinary.delete_image(product.img_url)
                    img_url: str = await cloudinary.upload_image(value)
                    product.img_url = img_url

                else:
                    setattr(product, key, value)

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product_id: int):
        product = self.get_by_id(product_id)

        if not product:
            return False

        cloudinary = Cloudinary()
        cloudinary.delete_image(product.img_url)

        self.session.delete(product)
        self.session.commit()
        return True
