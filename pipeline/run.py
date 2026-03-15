"""
pipeline/run.py
Orquestador principal del scraping.

Uso:
  # Descubrir torneos y scrapear todos
  python -m pipeline.run --all

  # Scrapear un torneo específico por su ID de BDFA
  python -m pipeline.run --tournament-id 5617

  # Scrapear últimos N torneos
  python -m pipeline.run --last 10
"""

import json
import logging
import argparse
from pathlib import Path
from tqdm import tqdm

from scrapers import BDFAScraper
from parsers import parse_tournament_page
from db import init_db, get_session
from db.loader import load_tournament_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TOURNAMENTS_FILE = Path("data/tournaments.json")


def load_tournament_list() -> list[dict]:
    if not TOURNAMENTS_FILE.exists():
        logger.info("tournaments.json no encontrado, descubriendo torneos...")
        from pipeline.discover_tournaments import main as discover
        discover()
    return json.loads(TOURNAMENTS_FILE.read_text())


def scrape_one(scraper: BDFAScraper, tournament_id: int, session) -> bool:
    try:
        raw = scraper.get_tournament_data(tournament_id)
        parsed = parse_tournament_page(raw["soup"], tournament_id, raw["url"])
        load_tournament_data(session, parsed)
        return True
    except Exception as e:
        logger.error(f"Error en torneo {tournament_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Pipeline de scraping — fútbol argentino")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Scrapear todos los torneos")
    group.add_argument("--tournament-id", type=int, help="ID de BDFA de un torneo específico")
    group.add_argument("--last", type=int, metavar="N", help="Scrapear los últimos N torneos")
    parser.add_argument("--no-cache", action="store_true", help="Ignorar caché local")
    args = parser.parse_args()

    # Inicializar DB
    init_db()

    scraper = BDFAScraper(use_cache=not args.no_cache)

    with next(get_session()) as session:

        if args.tournament_id:
            ok = scrape_one(scraper, args.tournament_id, session)
            print("OK" if ok else "FALLÓ")

        else:
            torneos = load_tournament_list()
            if args.last:
                torneos = torneos[-args.last:]

            ok_count = 0
            for t in tqdm(torneos, desc="Scrapeando torneos"):
                ok = scrape_one(scraper, t["id"], session)
                if ok:
                    ok_count += 1

            print(f"\nCompletado: {ok_count}/{len(torneos)} torneos cargados")


if __name__ == "__main__":
    main()
