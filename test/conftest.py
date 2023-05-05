from pathlib import Path
import pytest
from deuxpots import CERFA_VARIABLES_PATH, FAMILY_BOX_COORDS_PATH
from deuxpots.box import load_box_mapping

from deuxpots.pdf_tax_parser import load_family_box_coords


@pytest.fixture
def tax_sheet_pdf_path():
    return Path("declaration.pdf")


@pytest.fixture
def family_box_coords():
    return load_family_box_coords(FAMILY_BOX_COORDS_PATH)


@pytest.fixture
def box_mapping():
    return load_box_mapping(CERFA_VARIABLES_PATH)
