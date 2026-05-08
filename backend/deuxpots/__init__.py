from datetime import date
from os import environ
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.absolute()

DEV_MODE = not environ.get('FLY_APP_NAME')

CATEGORY_COORDS_PATH = ROOT_PATH / "resources/category_coords.json"
CERFA_VARIABLES_PATH = ROOT_PATH / "resources/cerfa_variables.json"

_SIMULATOR_URL_TEMPLATE = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-{year}.cgi"
_confirmed_urls = {}  # year -> url, only populated on successful HEAD


def get_simulator_url():
    import requests
    current_year = date.today().year
    if current_year not in _confirmed_urls:
        url = _SIMULATOR_URL_TEMPLATE.format(year=current_year)
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code < 400:
                _confirmed_urls[current_year] = url
        except requests.RequestException:
            pass
    return _confirmed_urls.get(current_year, _SIMULATOR_URL_TEMPLATE.format(year=current_year - 1))
