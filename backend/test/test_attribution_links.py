import pytest

from deuxpots.attribution_links import annotate_attribution_links, resolve_attribution_links
from deuxpots.flatbox import FlatBox


@pytest.mark.parametrize("box_codes,expected", [
    # Foncier au régime réel : la part étrangère suit les revenus fonciers, et la 8TK suit
    # la part étrangère.
    (['4BA', '4BL', '8TK'], {'4BL': ['4BA'], '8TK': ['4BL']}),
    # Micro-foncier : même chaîne avec 4BE / 4BK.
    (['4BE', '4BK', '8TK'], {'4BK': ['4BE'], '8TK': ['4BK']}),
    # Réel et micro cumulés : la 8TK suit les deux parts étrangères.
    (['4BA', '4BL', '4BE', '4BK', '8TK'],
     {'4BL': ['4BA'], '4BK': ['4BE'], '8TK': ['4BL', '4BK']}),
    # La CSG déductible et le prélèvement forfaitaire suivent les revenus qui les ont générés.
    (['2DC', '2TR', '2CK', '6DE'],
     {'2CK': ['2DC', '2TR'], '6DE': ['2DC', '2TR']}),
    # La CSG déductible tient compte du patrimoine mobilier ET foncier.
    (['2DC', '4BA', '6DE'], {'6DE': ['2DC', '4BA']}),
    # Une case suiveuse sans aucune meneuse présente n'est pas liée : rien à propager.
    (['8TK', '1AJ'], {}),
    (['6DE'], {}),
    # Aucune case liée.
    (['1AJ', '1BJ', '7DB'], {}),
])
def test_resolve_attribution_links(box_codes, expected):
    assert resolve_attribution_links(box_codes) == expected


def test_annotate_attribution_links():
    boxes = [FlatBox(code=code, raw_value=1000) for code in ['4BA', '4BL', '8TK', '1AJ']]
    annotated = {box.code: box.attribution_follows for box in annotate_attribution_links(boxes)}
    assert annotated == {
        '4BA': None,
        '4BL': ['4BA'],
        '8TK': ['4BL'],
        '1AJ': None,
    }


def test_no_box_follows_itself():
    """Une case ne doit jamais dépendre d'elle-même, sous peine de boucle de propagation."""
    for follower, leaders in resolve_attribution_links(
            ['2DC', '2TR', '2TS', '2BH', '2FU', '2CK', '4BA', '4BE', '4BL', '4BK', '6DE', '8TK']
    ).items():
        assert follower not in leaders
