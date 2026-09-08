export const createEmptyBox = () => ({
    code: "",
    raw_value: "",
    description: "",
    partner_0_value: "",
    partner_1_value: "",
    attribution: null,
    totalIsLocked: false
})

const precisionOf = (box) => (box.type === "float") ? .1 : 1

const round = (val, precision) => Math.round(val / precision) * precision

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
