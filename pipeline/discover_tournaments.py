import json
import logging
from pathlib import Path
from scrapers.bdfa import BDFAScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT = Path("data/tournaments.json")


def main():
    scraper = BDFAScraper(use_cache=True)
    torneos = scraper.get_tournament_ids()

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(torneos, ensure_ascii=False, indent=2))

    print(f"\n{len(torneos)} torneos encontrados → guardados en {OUTPUT}")
    print("\nPrimeros 5:")
    for t in torneos[:5]:
        print(f"  ID {t['id']:>6}  {t['nombre']}")
    print("\nÚltimos 5:")
    for t in torneos[-5:]:
        print(f"  ID {t['id']:>6}  {t['nombre']}")


if __name__ == "__main__":
    main()