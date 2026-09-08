export const createEmptyBox = () => ({
    code: "",
    raw_value: "",
    description: "",
    partner_0_value: "",
    partner_1_value: "",
    attribution: null,
    attribution_follows: null,
    totalIsLocked: false
})

const precisionOf = (box) => (box.type === "float") ? .1 : 1

const round = (val, precision) => Math.round(val / precision) * precision

const hasAttribution = (box) => (box.attribution || box.attribution === 0)

const hasValue = (box) => (box.raw_value || box.raw_value === 0)

/**
 * Applique une répartition à une case, et en déduit les montants des deux déclarant·e·s.
 *
 * Le montant du·de la déclarant·e 0 est pris comme complément de l'autre, et non arrondi
 * séparément : les deux montants s'additionnent ainsi toujours exactement au total.
 */
export const applyAttribution = (box, attribution) => {
    const precision = precisionOf(box)
    box.attribution = attribution
    box.partner_1_value = round(attribution * box.raw_value, precision)
    box.partner_0_value = round(box.raw_value - box.partner_1_value, precision)
    return box
}

/**
 * Pas du curseur de répartition.
 *
 * Le pas doit diviser le total, sinon l'extrémité droite du curseur est inatteignable : un
 * curseur poussé à fond s'arrête au dernier multiple du pas, et laisse un reliquat chez
 * l'autre déclarant·e (avec un total de 12 345 et un pas de 1 234, on plafonne à 12 340).
 *
 * On découpe donc en dixièmes du total, ce qui rend les deux extrémités atteignables et fait
 * tomber chaque cran sur un pourcentage rond.
 */
export const sliderStep = (box) => {
    if (box.type === "float") {
        // Nombres d'enfants : la déclaration ne connaît que les demi-parts.
        return .5
    }
    if (!box.raw_value || box.raw_value <= 10) {
        return 1
    }
    return box.raw_value / 10
}

/**
 * Marque une case comme répartie par l'utilisateur·rice : elle ne sera plus recalculée
 * automatiquement, même si les cases dont elle dépend changent.
 */
export const markAttributionAsManual = (box) => {
    box.attributionIsInherited = false
    return box
}

/**
 * Répartition héritée des cases meneuses, pondérée par leurs montants.
 *
 * Exemple : la CSG déductible (6DE) suit les revenus du patrimoine. Si ces revenus sont à 80 %
 * chez le·a déclarant·e 1 et à 20 % chez l'autre, la CSG l'est aussi.
 *
 * Renvoie null si aucune meneuse n'est encore répartie : il n'y a alors rien à propager.
 */
const inheritedAttribution = (box, boxesByCode) => {
    const leaders = (box.attribution_follows || [])
        .map(code => boxesByCode[code])
        .filter(leader => leader && hasAttribution(leader) && hasValue(leader))
    if (!leaders.length) {
        return null
    }
    const totalWeight = leaders.reduce((sum, leader) => sum + Math.abs(leader.raw_value), 0)
    if (!totalWeight) {
        // Des meneuses toutes à zéro : leurs montants ne peuvent pas départager, on fait
        // la moyenne simple de leurs répartitions.
        return leaders.reduce((sum, leader) => sum + leader.attribution, 0) / leaders.length
    }
    return leaders.reduce(
        (sum, leader) => sum + leader.attribution * Math.abs(leader.raw_value), 0
    ) / totalWeight
}

/**
 * Propose une répartition pour les cases qui dépendent d'une autre (voir attribution_links
 * côté serveur), à partir de celles déjà réparties.
 *
 * Une case modifiée à la main n'est jamais écrasée. La propagation est transitive : répartir
 * les revenus fonciers (4BA) renseigne la part étrangère (4BL), qui renseigne à son tour la
 * case 8TK.
 */
export const propagateAttributions = (boxes) => {
    const boxesByCode = {}
    boxes.forEach(box => {
        if (box.code) {
            boxesByCode[box.code] = box
        }
    })

    const isOpenToInheritance = (box) => (
        box.code
        && box.type !== "bool"
        && box.attributionIsInherited !== false
        && hasValue(box)
        && box.attribution_follows
        && box.attribution_follows.length
    )

    // Une passe de propagation. Renvoie vrai si au moins une case a été renseignée.
    const propagateOnce = () => {
        let hasChanged = false
        for (const box of boxes) {
            if (!isOpenToInheritance(box)) {
                continue
            }
            const attribution = inheritedAttribution(box, boxesByCode)
            if (attribution === null || attribution === box.attribution) {
                continue
            }
            applyAttribution(box, attribution)
            box.attributionIsInherited = true
            hasChanged = true
        }
        return hasChanged
    }

    // La propagation est transitive : on itère jusqu'à stabilisation. Le garde-fou borne le
    // nombre de passes à la longueur d'une chaîne de dépendances possible.
    let passes = 0
    while (passes <= boxes.length && propagateOnce()) {
        passes += 1
    }
    return boxes
}
