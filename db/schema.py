"""
db/schema.py
Modelos SQLAlchemy — tablas de la base de datos.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Torneo(Base):
    __tablename__ = "torneos"

    id           = Column(Integer, primary_key=True)
    bdfa_id      = Column(Integer, unique=True, nullable=False, index=True)
    nombre       = Column(String, nullable=False)
    nombre_norm  = Column(String)   # "apertura", "clausura", "anual"
    anio         = Column(Integer, index=True)
    url          = Column(String)
    scrapeado_en = Column(DateTime, default=datetime.utcnow)

    posiciones = relationship("Posicion", back_populates="torneo", cascade="all, delete-orphan")
    goleadores = relationship("Goleador", back_populates="torneo", cascade="all, delete-orphan")


class Equipo(Base):
    __tablename__ = "equipos"

    id        = Column(Integer, primary_key=True)
    bdfa_id   = Column(Integer, unique=True, nullable=True, index=True)
    nombre    = Column(String, nullable=False, unique=True)
    ciudad    = Column(String)
    estadio   = Column(String)

    posiciones = relationship("Posicion", back_populates="equipo")
    goles_como_goleador = relationship("Goleador", back_populates="equipo")


class Posicion(Base):
    __tablename__ = "posiciones"
    __table_args__ = (
        UniqueConstraint("torneo_id", "equipo_id", name="uq_posicion_torneo_equipo"),
        Index("ix_posicion_torneo", "torneo_id"),
        Index("ix_posicion_equipo", "equipo_id"),
    )

    id               = Column(Integer, primary_key=True)
    torneo_id        = Column(Integer, ForeignKey("torneos.id"), nullable=False)
    equipo_id        = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    posicion         = Column(Integer)
    partidos_jugados = Column(Integer, default=0)
    ganados          = Column(Integer, default=0)
    empatados        = Column(Integer, default=0)
    perdidos         = Column(Integer, default=0)
    goles_favor      = Column(Integer, default=0)
    goles_contra     = Column(Integer, default=0)
    diferencia_goles = Column(Integer, default=0)
    puntos           = Column(Integer, default=0)

    torneo = relationship("Torneo", back_populates="posiciones")
    equipo = relationship("Equipo", back_populates="posiciones")


class Goleador(Base):
    __tablename__ = "goleadores"
    __table_args__ = (
        UniqueConstraint("torneo_id", "jugador_bdfa_id", name="uq_goleador_torneo_jugador"),
    )

    id               = Column(Integer, primary_key=True)
    torneo_id        = Column(Integer, ForeignKey("torneos.id"), nullable=False)
    equipo_id        = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    jugador_nombre   = Column(String, nullable=False)
    jugador_bdfa_id  = Column(Integer, nullable=True)
    goles            = Column(Integer, nullable=False)

    torneo = relationship("Torneo", back_populates="goleadores")
    equipo = relationship("Equipo", back_populates="goles_como_goleador")