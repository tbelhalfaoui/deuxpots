import { applyAttribution, markAttributionAsManual, propagateAttributions, sliderStep } from "./box.js";

test("le pas du curseur divise toujours le total, pour que les extrémités soient atteignables", () => {
    // Un pas qui ne divise pas le total rend l'extrémité droite inatteignable : le curseur
    // poussé à fond s'arrêtait au dernier multiple du pas.
    [12345, 3333, 50000, 100, 11, 7, 1].forEach(raw_value => {
        const step = sliderStep({ raw_value })
        const maxReachable = Math.floor(raw_value / step) * step
        expect(maxReachable).toBeCloseTo(raw_value)
    })
})

test("le curseur des nombres d'enfants reste au demi-point", () => {
    expect(sliderStep({ raw_value: 2, type: "float" })).toBe(.5)
})

test("le pas reste valide pour une case sans montant", () => {
    expect(sliderStep({ raw_value: 0 })).toBe(1)
    expect(sliderStep({ raw_value: "" })).toBe(1)
})

test("pousser le curseur à fond attribue la totalité à un·e seul·e déclarant·e", () => {
    const box = { code: "4BA", raw_value: 12345, attribution: null }
    applyAttribution(box, 1)
    expect(box.partner_0_value).toBe(0)
    expect(box.partner_1_value).toBe(12345)

    applyAttribution(box, 0)
    expect(box.partner_0_value).toBe(12345)
    expect(box.partner_1_value).toBe(0)
})

test("les deux montants s'additionnent toujours au total", () => {
    // Un arrondi séparé des deux montants pouvait les faire dépasser le total d'une unité.
    const box = { code: "4BA", raw_value: 12345 }
    for (let tenth = 0; tenth <= 10; tenth++) {
        applyAttribution(box, tenth / 10)
        expect(box.partner_0_value + box.partner_1_value).toBe(12345)
    }
})

test("respecte le demi-point sur les cases en nombre d'enfants", () => {
    const box = { code: "0CF", raw_value: 3, type: "float" }
    applyAttribution(box, 1 / 3)
    expect(box.partner_0_value + box.partner_1_value).toBe(3)
})


const box = (code, raw_value, extra = {}) => ({
    code,
    raw_value,
    partner_0_value: "",
    partner_1_value: "",
    attribution: null,
    attribution_follows: null,
    ...extra
})

test("propage la répartition d'une case vers celle qui en dépend", () => {
    const boxes = propagateAttributions([
        box("4BA", 10000, { attribution: .25 }),
        box("4BL", 8000, { attribution_follows: ["4BA"] }),
    ])
    expect(boxes[1].attribution).toBe(.25)
    expect(boxes[1].partner_0_value).toBe(6000)
    expect(boxes[1].partner_1_value).toBe(2000)
})

test("propage de façon transitive le long de la chaîne de dépendances", () => {
    const boxes = propagateAttributions([
        // Volontairement dans l'ordre inverse de la chaîne, pour vérifier que l'ordre
        // des cases n'influe pas sur le résultat.
        box("8TK", 12000, { attribution_follows: ["4BL"] }),
        box("4BL", 8000, { attribution_follows: ["4BA"] }),
        box("4BA", 10000, { attribution: 1 }),
    ])
    expect(boxes.map(b => b.attribution)).toEqual([1, 1, 1])
})

test("pondère la répartition héritée par le montant des cases meneuses", () => {
    // 9 000 € entièrement au déclarant 1, 1 000 € entièrement au déclarant 0
    // -> 90 % pour le déclarant 1.
    const boxes = propagateAttributions([
        box("2DC", 9000, { attribution: 1 }),
        box("4BA", 1000, { attribution: 0 }),
        box("6DE", 500, { attribution_follows: ["2DC", "4BA"] }),
    ])
    expect(boxes[2].attribution).toBeCloseTo(.9)
    expect(boxes[2].partner_1_value).toBe(450)
})

test("n'écrase pas une case répartie à la main", () => {
    const manual = markAttributionAsManual(
        box("4BL", 8000, { attribution: .5, attribution_follows: ["4BA"] })
    )
    const boxes = propagateAttributions([box("4BA", 10000, { attribution: 1 }), manual])
    expect(boxes[1].attribution).toBe(.5)
})

test("ne propose rien tant que la case meneuse n'est pas répartie", () => {
    const boxes = propagateAttributions([
        box("4BA", 10000),
        box("4BL", 8000, { attribution_follows: ["4BA"] }),
    ])
    expect(boxes[1].attribution).toBeNull()
    expect(boxes[1].partner_0_value).toBe("")
})

test("ignore une case meneuse absente de la déclaration", () => {
    const boxes = propagateAttributions([
        box("8TK", 12000, { attribution_follows: ["4BL"] }),
    ])
    expect(boxes[0].attribution).toBeNull()
})

test("laisse les cases sans dépendance intactes", () => {
    const boxes = propagateAttributions([
        box("4BA", 10000, { attribution: .25 }),
        box("7DB", 2000),
    ])
    expect(boxes[1].attribution).toBeNull()
})
