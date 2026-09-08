"""
Liens d'attribution entre cases.

Certaines cases de la déclaration n'existent qu'en un seul exemplaire pour le foyer
(BoxKind.COMMON) : la déclaration ne dit jamais à qui elles appartiennent, donc l'outil ne peut
pas les attribuer automatiquement et les laisse à l'utilisateur.

Mais toutes ces cases ne sont pas indépendantes. Certaines ne sont que le détail ou la
conséquence d'une autre : la répartition des revenus fonciers de source étrangère (4BL) est
forcément celle des revenus fonciers (4BA) dont ils sont un sous-ensemble ; la CSG déductible
(6DE) suit les revenus du patrimoine qui l'ont générée.

On décrit ici ces dépendances pour proposer une répartition par défaut cohérente. Il ne s'agit
pas de deviner une information absente de la déclaration, mais de propager un arbitrage que
l'utilisateur a déjà fait sur la case principale. La proposition reste modifiable.
"""

from typing import Dict, List, Tuple


# Revenus des valeurs et capitaux mobiliers, dans l'ordre de préférence.
CAPITAL_INCOME_BOXES = ('2DC', '2TR', '2TS', '2BH', '2FU')

# Revenus fonciers : régime réel (4BA) et micro-foncier (4BE).
PROPERTY_INCOME_BOXES = ('4BA', '4BE')

# Une case suiveuse hérite de la répartition de ses cases meneuses, pondérée par leur montant.
# Seules les meneuses effectivement présentes dans la déclaration sont retenues.
ATTRIBUTION_LINKS: Dict[str, Tuple[str, ...]] = {
    # "Dont revenus de source étrangère" : sous-ensemble des revenus fonciers correspondants.
    '4BL': ('4BA',),
    '4BK': ('4BE',),
    # Revenus étrangers ouvrant droit à un crédit d'impôt égal à l'impôt français. Les attribuer
    # comme le foncier étranger évite l'incohérence que le simulateur rejette
    # ("4 BK, 4 BL, RBK, RBT SANS SAISIE DE 8TK").
    '8TK': ('4BL', '4BK'),
    # Prélèvement forfaitaire non libératoire déjà versé sur les revenus de capitaux mobiliers.
    '2CK': CAPITAL_INCOME_BOXES,
    # CSG déductible calculée sur les revenus du patrimoine : elle suit ces revenus.
    '6DE': CAPITAL_INCOME_BOXES + PROPERTY_INCOME_BOXES,
}


def resolve_attribution_links(box_codes) -> Dict[str, List[str]]:
    """
    Restreint la table des liens aux cases réellement présentes dans la déclaration.

    Une case suiveuse n'est retenue que si au moins une de ses meneuses est présente, et une
    case ne peut pas se suivre elle-même.
    """
    present = set(box_codes)
    links = {}
    for follower, leaders in ATTRIBUTION_LINKS.items():
        if follower not in present:
            continue
        present_leaders = [leader for leader in leaders
                           if leader in present and leader != follower]
        if present_leaders:
            links[follower] = present_leaders
    return links


def annotate_attribution_links(flat_boxes):
    """
    Renseigne le champ `attribution_follows` de chaque case, à partir des cases présentes.
    """
    links = resolve_attribution_links(box.code for box in flat_boxes)
    for box in flat_boxes:
        box.attribution_follows = links.get(box.code)
    return flat_boxes
