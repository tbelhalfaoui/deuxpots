from warnings import warn

import pytest
from deuxpots.pdf_tax_parser import FamilyBoxExtractionWarning, HouseholdStatusWarning
from deuxpots.warning_error_utils import UserFacingWarning, handle_warnings


def test_handle_warnings():
    @handle_warnings(UserFacingWarning)
    def some_flask_route():
        warn(FamilyBoxExtractionWarning("message 1"))
        warn(HouseholdStatusWarning("message 2"))
        warn(HouseholdStatusWarning())
        warn(Warning("other message"))
        return {"results": "ok"}

    with pytest.warns(FamilyBoxExtractionWarning):
        res = some_flask_route()
    with pytest.warns(HouseholdStatusWarning):
        res = some_flask_route()
    with pytest.warns(Warning):
        res = some_flask_route()
    
    assert res == {
        "results": "ok",
        "warnings": ["message 1", "message 2", "HouseholdStatusWarning"]
    }
