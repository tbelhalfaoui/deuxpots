from warnings import warn

import pytest
from deuxpots.pdf_tax_parser import FamilyBoxNotExtracted, BadHouseholdStatus
from deuxpots.warning_error_utils import UserFacingWarning, handle_warnings


def test_handle_warnings():
    @handle_warnings(UserFacingWarning)
    def some_flask_route():
        warn(FamilyBoxNotExtracted(["1AA", "2BB"]))
        warn(BadHouseholdStatus(["C", "V"]))
        warn(Warning("other message"))
        return {"results": "ok"}

    with pytest.warns(FamilyBoxNotExtracted):
        res = some_flask_route()
    with pytest.warns(BadHouseholdStatus):
        res = some_flask_route()
    with pytest.warns(Warning):
        res = some_flask_route()
    
    assert res == {
        'results': 'ok',
        'warnings': [("Certaines cases concernant la situation du foyer fiscal et les personnes à charge n'ont pas bien été détectées (1AA, 2BB). "
                      "Merci de les renseigner manuellement."),
                     ('La case "situation du foyer fiscal" n\'a pas été correctement détectée (C, V). '
                      'Merci de vérifier qu\'il s\'agit bien une déclaration commune (marié·e·s ou pacsé·e·s).')]
    }
