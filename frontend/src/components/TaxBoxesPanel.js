import { useState } from "react"
import { TaxBox } from './TaxBox.js'

export const TaxBoxesPanel = ({boxes, setBoxes}) => {

    const [modifyTotals, setModifyTotals] = useState(false);

    const onBoxChange = async (evt) => {
        let boxCode, fieldName;
        [boxCode, fieldName] = evt.target.name.split('.');

        let boxesNew = { ...boxes };
        var value = parseInt(evt.target.value.replace(' ', ''));

        if (fieldName == 'slider') {
            boxesNew[boxCode].ratio_0 = 1 - value / boxesNew[boxCode].raw_value;
            console.log(boxesNew[boxCode].raw_value);
        }
        else if (isNaN(value)) {
            value = "";
        }
        boxesNew[boxCode][fieldName] = value;
        
        if (fieldName == 'partner_0_value') {
            if (!modifyTotals) {
                boxesNew[boxCode]['partner_1_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_0_value']);
            }
            else {
                boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio_0']) * boxesNew[boxCode]['raw_value']);
                boxesNew[boxCode]['raw_value'] = Math.round(boxesNew[boxCode]['partner_0_value'] + boxesNew[boxCode]['partner_1_value']);
            }
            boxesNew[boxCode]['ratio_0'] = Math.round(boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value']);
        }
        else if (fieldName == 'partner_1_value') {
            if (!modifyTotals) {
                boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_1_value']);
            }
            else {
                boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio_0'] * boxesNew[boxCode]['raw_value']);
                boxesNew[boxCode]['raw_value'] = Math.round(boxesNew[boxCode]['partner_0_value'] + boxesNew[boxCode]['partner_1_value']);
            }
            boxesNew[boxCode]['ratio_0'] = Math.round(boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value']);
        }
        if (fieldName == 'slider') {
            boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio_0'] * boxesNew[boxCode]['raw_value']);
            boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio_0']) * boxesNew[boxCode]['raw_value']);
        }
        if (fieldName == 'raw_value') {
            boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio_0'] * boxesNew[boxCode]['raw_value']);
            boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio_0']) * boxesNew[boxCode]['raw_value']);
        }
        
        setBoxes(boxesNew);
    };

    const toggleModifyTotals = async (evt) => {
        setModifyTotals(evt.target.checked);
    };

    const boxesUnattributed = Object.values(boxes).filter(
        box => box.ratio_0 == null
    );

    const boxesAttributed = Object.values(boxes).filter(
        box => box.ratio_0 != null
    );

    return (
    <form>
        <div id="containerStep2" class="container py-2 text-start">
            <div class="form-check form-switch py-2">
                <input class="form-check-input" type="checkbox" role="switch" id="modifyTotals" checked={modifyTotals} onChange={toggleModifyTotals} />
                <label class="form-check-label" for="modifyTotals">Modifier les totaux</label>
            </div>
            <div class="accordion" id="accordionBoxes">
                {boxesUnattributed.length > 0 && (
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingManualBoxes">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseManualBoxes" aria-expanded="true" aria-controls="collapseManualBoxes">
                            Cases communes, à attribuer manuellement.
                            </button>
                        </h2>
                        <div id="collapseManualBoxes" class="accordion-collapse collapse show"
                        aria-labelledby="headingManualBoxes" data-bs-parent="#accordionBoxes">
                            <div class="accordion-body">
                                {boxesUnattributed.map((box) => (
                                    <TaxBox box={box} onChange={onBoxChange} modifyTotals={modifyTotals} />
                                ))}
                            </div>
                        </div>
                    </div>
                )}
                {boxesAttributed.length > 0 && (
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingAutoBoxes">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseAutoBoxes" aria-expanded="false" aria-controls="collapseAutoBoxes">
                            Cases séparées, attribuées automatiquement.
                            </button>
                        </h2>
                        <div id="collapseAutoBoxes" class="accordion-collapse collapse" aria-labelledby="headingAutoBoxes"
                        data-bs-parent="#accordionBoxes">
                            <div class="accordion-body">
                            <div class="row text-center">
                                <div class="col-1"><h6>Total</h6></div>
                                <div class="col-1"><h6>Déclarant·e 1</h6></div>
                                <div class="col-2"><h6>Répartition</h6></div>
                                <div class="col-1"><h6>Déclarant·e 2</h6></div>
                            </div>
                                {boxesAttributed.map(box => (
                                    <TaxBox box={box} onChange={onBoxChange} modifyTotals={modifyTotals} />
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    </form>
);
}