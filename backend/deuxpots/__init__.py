from os import environ
from pathlib import Path
from datetime import date
import requests as rq

ROOT_PATH = Path(__file__).parent.parent.absolute()

DEV_MODE = not environ.get('FLY_APP_NAME')

CATEGORY_COORDS_PATH = ROOT_PATH / "resources/category_coords.json"
CERFA_VARIABLES_PATH = ROOT_PATH / "resources/cerfa_variables.json"

SIMULATOR_URL_TEMPLATE = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-{year}.cgi"


def _make_simulator_url():
    current_year = date.today().year
    try:
        url = SIMULATOR_URL_TEMPLATE.format(year=current_year)
        rq.head(url, timeout=5).raise_for_status()
        return url
    except rq.RequestException:
        return SIMULATOR_URL_TEMPLATE.format(year=current_year - 1)


SIMULATOR_URL = _make_simulator_url()
