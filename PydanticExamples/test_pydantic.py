from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from venv import logger


class User(BaseModel):  # Создается класс User с помощью BaseModel от pydantic и указывается
    name: str       # что имя должно быть строкой
    age: int        # возраст должен быть числом
    adult: bool     # поле совершенолетие должно быть булевым значением


def get_user():  # функция get_user возвращает обьект dict с следущими полями
    return {
        "name": "Alice",
        "age": 25,
        "adult": "true"
    }


def test_user_data():
    user = User(**get_user())  # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    assert user.name == "Alice"  # Возможность дополнительных проверок
    logger.info(f"{user.name=} {user.age=} {user.adult=}")  # а также возможность удобного взаимодействия


class ProductType(str, Enum):
    NEW = "new"
    PREVIOUS_USE = "previous_use"


class Manufacturer(BaseModel):
    name: str
    city: Optional[str] = None
    street: Optional[str] = None


class Product(BaseModel):
    # поле name может иметь длину в диапазоне от 3 до 50 символов и является строкой
    name: str = Field(..., min_length=3, max_length=50, description="Название продукта")
    # поле price должно быть больше 0
    price: float = Field(..., gt=0, description="Цена продукта")
    # поле in_stock принимает булево значение и установится по умолчанию = False
    in_stock: bool = Field(default=False, description="Есть ли в наличии")
    # поле color должно быть строкой и принимает значение "black" по умолчанию
    color: str = Field(default="black", description="Цвет")
    # поле year не обязательное. можно не указывать при создании обьекта
    year: Optional[int] = None
    # поле product принимает тип Enum (может содержать только 1 из его значений)
    product: ProductType
    # поле manufacturer принимает тип другой BaseModel
    manufacturer: Manufacturer


def test_product():
    # Пример создания обьекта + в поле price передаём строку вместо числа
    product = Product(name="Laptop", price="999.99", product=ProductType.NEW, manufacturer=Manufacturer(name="MSI"))
    logger.info(f"{product=}")
    # Output: product=Product(name='Laptop', price=999.99, in_stock=False, color='black', year=None, product=<ProductType.NEW: 'new'>, manufacturer=Manufacturer(name='MSI', city=None, street=None))

    # Пример конвертации обьекта в json
    json_data = product.model_dump_json(exclude_unset=True)
    logger.info(f"{json_data=}")
    # Output: json_data='{"name":"Laptop","price":999.99,"product":"new","manufacturer":{"name":"MSI"}}'

    # Пример конвертации json в обьект
    new_product = Product.model_validate_json(json_data)
    logger.info(f"{new_product=}")
    # Output: new_product=Product(name='Laptop', price=999.99, in_stock=False, color='black', year=None, product=<ProductType.NEW: 'new'>, manufacturer=Manufacturer(name='MSI', city=None, street=None))

class User2(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

def test_model_json_schema():
    # Генерируем JSON Schema
    user_schema = User2.model_json_schema()
    logger.info(user_schema)
    #Output:
    #{
    #    'properties':
    #    {
    #        'id':{'title': 'Id', 'type': 'integer'},
    #        'name':  {'title': 'Name', 'type': 'string'},
    #        'email': {'title': 'Email', 'type': 'string'},
    #        'is_active': {'default': True, 'title': 'Is Active', 'type': 'boolean'}
    #    },
    #    'required': ['id', 'name', 'email'],
    #    'title': 'User2', 'type': 'object'
    #}
