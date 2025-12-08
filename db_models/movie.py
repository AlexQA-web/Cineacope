from typing import Dict, Any

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MovieDBModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    image_url = Column(String)
    location = Column(String)
    published = Column(Boolean)
    rating = Column(Integer)
    genre_id = Column(String)
    created_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'imageUrl': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<User(id='{self.id}', name='{self.name}')>"
