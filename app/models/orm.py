from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey
from app.models.db import Base

class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    about: Mapped[str] = mapped_column(Text, nullable=True)

    products = relationship("ProductORM", back_populates="brand")


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    handle: Mapped[str] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    price: Mapped[str] = mapped_column(String(50), nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, default=None)
    image: Mapped[str] = mapped_column(String(500), nullable=True)

    brand = relationship("Brand", back_populates="products")
