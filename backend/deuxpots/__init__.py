from os import environ
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.absolute()

DEV_MODE = not environ.get('FLY_APP_NAME')

CATEGORY_COORDS_PATH = ROOT_PATH / "resources/category_coords.json"
CERFA_VARIABLES_PATH = ROOT_PATH / "resources/cerfa_variables.json"

SIMULATOR_URL = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-2024.cgi"
