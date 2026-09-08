import { applyAttribution, sliderStep } from "./box.js";

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
