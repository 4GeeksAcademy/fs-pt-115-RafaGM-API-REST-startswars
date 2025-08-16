from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

favorites_table = Table(
    "favorites",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("character_id", ForeignKey("characters.id")),
    Column("vehiculo_id", ForeignKey("vehiculo.id"))
)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    firstname: Mapped[str] = mapped_column(String(120), nullable=False)
    lastname: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    favorites: Mapped[List["Characters"]] = relationship("Character", secondary = favorites_table, back_populates = "favorites_by")
    favorites: Mapped[List["Vehiculo"]] = relationship("Vehiculo", secondary = favorites_table, back_populates = "favorites_by")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "favorites": [characters.serialize() for characters in self.favorites],
            "favorites": [Vehiculo.serialize() for Vehiculo in self.favorites]
        }

class Characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    birth_year: Mapped[int] = mapped_column(nullable=False)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)

    favorite_by: Mapped[List["User"]] = relationship ("user", secondary = favorites_table, back_populates = "favorites")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "eye_color": self.eye_color,
            "gender": self.gender
        }

class Vehiculo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    model : Mapped[str] = mapped_column(String(50), nullable=False)
    length : Mapped[int] = mapped_column(nullable=False)

    favorite_by: Mapped[List["User"]] = relationship ("user", secondary = favorites_table, back_populates = "favorites")
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "length": self.length,
        }