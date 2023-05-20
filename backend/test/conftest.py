from pathlib import Path
import pytest
from deuxpots import ROOT_PATH
from deuxpots import CERFA_VARIABLES_PATH, CATEGORY_COORDS_PATH
from deuxpots.box import load_box_mapping

from deuxpots.pdf_tax_parser import load_category_coords


@pytest.fixture
def tax_sheet_pdf_path():
    return ROOT_PATH / "test/resources/declaration.pdf"


@pytest.fixture
def tax_sheet_pdf_path_with_problems():
    return ROOT_PATH / "test/resources/declaration_with_problems.pdf"


@pytest.fixture
def category_coords():
    return load_category_coords(CATEGORY_COORDS_PATH)


@pytest.fixture
def box_mapping():
    return load_box_mapping(CERFA_VARIABLES_PATH)
