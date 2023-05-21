from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.absolute()

CATEGORY_COORDS_PATH = ROOT_PATH / "resources/category_coords.json"
CERFA_VARIABLES_PATH = ROOT_PATH / "resources/cerfa_variables.json"

SIMULATOR_URL = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-2023.cgi"
