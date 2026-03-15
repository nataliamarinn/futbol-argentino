"""
db/loader.py
Toma los datos parseados y los carga/actualiza en la base de datos.
Usa upsert para que sea seguro re-correr sin duplicar datos.
"""

import logging
from sqlalchemy.orm import Session
from .schema import Torneo, Equipo, Posicion, Goleador
from parsers.models import (
    Torneo as TorneoModel,
    PosicionEquipo as PosicionModel,
    Goleador as GoleadorModel,
)

logger = logging.getLogger(__name__)


def upsert_torneo(session: Session, t: TorneoModel) -> Torneo:
    obj = session.query(Torneo).filter_by(bdfa_id=t.bdfa_id).first()
    if not obj:
        obj = Torneo(bdfa_id=t.bdfa_id)
        session.add(obj)
    obj.nombre      = t.nombre
    obj.nombre_norm = t.nombre_normalizado
    obj.anio        = t.anio
    obj.url         = t.url
    session.flush()
    return obj


def upsert_equipo(session: Session, nombre: str, bdfa_id=None, ciudad=None) -> Equipo:
    # Buscar por bdfa_id si lo tenemos, sino por nombre
    obj = None
    if bdfa_id:
        obj = session.query(Equipo).filter_by(bdfa_id=bdfa_id).first()
    if not obj:
        obj = session.query(Equipo).filter_by(nombre=nombre).first()
    if not obj:
        obj = Equipo(nombre=nombre)
        session.add(obj)
    if bdfa_id and not obj.bdfa_id:
        obj.bdfa_id = bdfa_id
    if ciudad and not obj.ciudad:
        obj.ciudad = ciudad
    session.flush()
    return obj


def load_tournament_data(session: Session, parsed: dict):
    """
    Carga en la DB los datos retornados por parse_tournament_page().
    parsed = {"torneo": TorneoModel, "posiciones": [...], "goleadores": [...]}
    """
    torneo_db = upsert_torneo(session, parsed["torneo"])
    logger.info(f"Torneo: {torneo_db.nombre} ({torneo_db.anio}) — id={torneo_db.id}")

    # --- Posiciones ---
    for p in parsed["posiciones"]:
        equipo_db = upsert_equipo(
            session, p.equipo_nombre,
            bdfa_id=p.equipo_bdfa_id,
            ciudad=p.ciudad
        )
        pos = (
            session.query(Posicion)
            .filter_by(torneo_id=torneo_db.id, equipo_id=equipo_db.id)
            .first()
        )
        if not pos:
            pos = Posicion(torneo_id=torneo_db.id, equipo_id=equipo_db.id)
            session.add(pos)
        pos.posicion         = p.posicion
        pos.partidos_jugados = p.partidos_jugados
        pos.ganados          = p.ganados
        pos.empatados        = p.empatados
        pos.perdidos         = p.perdidos
        pos.goles_favor      = p.goles_favor
        pos.goles_contra     = p.goles_contra
        pos.diferencia_goles = p.diferencia_goles
        pos.puntos           = p.puntos

    # --- Goleadores ---
    for g in parsed["goleadores"]:
        gol = (
            session.query(Goleador)
            .filter_by(torneo_id=torneo_db.id, jugador_bdfa_id=g.jugador_bdfa_id)
            .first()
        ) if g.jugador_bdfa_id else None

        if not gol:
            gol = Goleador(
                torneo_id=torneo_db.id,
                jugador_nombre=g.jugador_nombre,
                jugador_bdfa_id=g.jugador_bdfa_id,
                goles=g.goles,
            )
            session.add(gol)
        else:
            gol.goles = g.goles

    session.commit()
    logger.info(f"  {len(parsed['posiciones'])} equipos, {len(parsed['goleadores'])} goleadores cargados")