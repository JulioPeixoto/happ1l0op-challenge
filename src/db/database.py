from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from src.settings import DATABASE_URL


sql_engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)


def create_tables():
    SQLModel.metadata.create_all(sql_engine)


def get_session() -> Generator[Session, None, None]:
    with Session(sql_engine) as session:
        yield session


def seed_initial_data():
    from src.model.product import Product
    
    with Session(sql_engine) as session:
        existing_products = session.query(Product).first()
        if existing_products:
            return

        initial_products = [
            Product(
                name="Coca-Cola",
                sku="COKE_350",
                description="Coca-Cola 350ml",
                price=3.50,
                stock_quantity=20,
            ),
            Product(
                name="Pepsi",
                sku="PEPSI_350",
                description="Pepsi 350ml",
                price=3.00,
                stock_quantity=15,
            ),
            Product(
                name="Sprite",
                sku="SPRITE_350",
                description="Sprite 350ml",
                price=3.25,
                stock_quantity=18,
            ),
            Product(
                name="Fanta Orange",
                sku="FANTA_350",
                description="Fanta Orange 350ml",
                price=3.25,
                stock_quantity=12,
            ),
            Product(
                name="Guarana Antarctica",
                sku="GUARANA_350",
                description="Guarana Antarctica 350ml",
                price=3.75,
                stock_quantity=10,
            ),
        ]

        for product in initial_products:
            session.add(product)

        session.commit()
        print("Initial products added to database!")
