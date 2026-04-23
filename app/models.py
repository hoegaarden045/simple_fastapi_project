from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from app.enums import CurrencyEnum


class User(Base):
    __tablename__ = "user"  # название таблицы в бд

    # mapped трансилирует тд в python в тд в sql (int в INTEGER, str в VARCHAR)
    # mapped_colummn задает валидацию данных
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[Decimal]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    currency: Mapped[CurrencyEnum]


class Operation(Base):
    __tablename__ = "operation"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    type: Mapped[str]
    amount: Mapped[Decimal]
    currency: Mapped[CurrencyEnum]
    category: Mapped[str | None] = mapped_column(default=None)
    subcategory: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
