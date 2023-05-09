import { useState } from "react"
import { TaxBox } from './TaxBox.js'

export const TaxBoxesPanel = ({boxes, setBoxes, setStep}) => {

    const [ showAutoFilled, setShowAutoFilled ] = useState(false);
    const [ unlockTotals, setUnlockTotals ] = useState(false);

    const onSliderChange = async (evt) => {
        var value = evt.target.value;
        const boxCode = evt.target.name.split('.')[0];
        if (isNaN(value)) {
            value = "";
        }
        let boxesNew = { ...boxes };
        boxesNew[boxCode].ratio = 1 - value / boxesNew[boxCode].raw_value;
        boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio'] * boxesNew[boxCode]['raw_value']);
        boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio']) * boxesNew[boxCode]['raw_value']);
        setBoxes(boxesNew);
    }

    const initializeBoxValues = () => {
        // let boxesNew = { ...boxes };
        // boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio'] * boxesNew[boxCode]['raw_value']);
        // boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio']) * boxesNew[boxCode]['raw_value']);
        // boxesNew[boxCode]['ratio'] = boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value'];
        // setBoxes(boxesNew);
    }

    const handleBoxChange = async (boxCode, fieldName, value) => {
        let boxesNew = { ...boxes };
        boxesNew[boxCode][fieldName] = value;
        
        if (fieldName == 'partner_0_value') {
            if (!unlockTotals) {
                boxesNew[boxCode]['partner_1_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_0_value']);
            }
            else {
                boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio']) * boxesNew[boxCode]['raw_value']);
                boxesNew[boxCode]['raw_value'] = Math.round(boxesNew[boxCode]['partner_0_value'] + boxesNew[boxCode]['partner_1_value']);
            }
            boxesNew[boxCode]['ratio'] = boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value'];
        }
        else if (fieldName == 'partner_1_value') {
            if (!unlockTotals) {
                boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_1_value']);
            }
            else {
                boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio'] * boxesNew[boxCode]['raw_value']);
                boxesNew[boxCode]['raw_value'] = Math.round(boxesNew[boxCode]['partner_0_value'] + boxesNew[boxCode]['partner_1_value']);
            }
            boxesNew[boxCode]['ratio'] = boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value'];
        }
        if (fieldName == 'raw_value') {
            boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['ratio'] * boxesNew[boxCode]['raw_value']);
            boxesNew[boxCode]['partner_1_value'] = Math.round((1 - boxesNew[boxCode]['ratio']) * boxesNew[boxCode]['raw_value']);
            boxesNew[boxCode]['ratio'] = boxesNew[boxCode]['partner_0_value'] / boxesNew[boxCode]['raw_value'];
        }        
        setBoxes(boxesNew);
    }

    const onBoxChange = async (values, sourceInfo) => {
        const evt = sourceInfo.event;
        const [boxCode, fieldName] = evt.target.name.split('.');
        handleBoxChange(boxCode, fieldName, values.floatValue)
    };

    const toggleShowAutofilled = async (evt) => {
        setShowAutoFilled(evt.target.checked);
    };

    const toggleUnlockTotals = async (evt) => {
        setUnlockTotals(evt.target.checked);
    };
    
    return (
        <form>
            <div id="containerStep2" class="container py-2 text-start">
                <div>
                    <div>
                        <div class="form-check form-switch py-2">
                            <input class="form-check-input" type="checkbox" role="switch" id="showAutofilled" checked={showAutoFilled} onChange={toggleShowAutofilled} />
                            <label class="form-check-label" for="showAutofilled">Afficher les cases préremplies.</label>
                        </div>
                        <div class="form-check form-switch py-2">
                            <input class="form-check-input" type="checkbox" role="switch" id="unlockTotals" checked={unlockTotals} onChange={toggleUnlockTotals} />
                            <label class="form-check-label" for="unlockTotals">Déverrouiller les totaux.</label>
                        </div>
                        <div class="row text-center">
                            <div class="col-1"><h6>Total</h6></div>
                            <div class="col-1"><h6>Déclarant·e 1</h6></div>
                            <div class="col-2"><h6>Répartition</h6></div>
                            <div class="col-1"><h6>Déclarant·e 2</h6></div>
                        </div>
                            {Object.values(boxes).map(box => (
                                <TaxBox box={box} onValueChange={onBoxChange} onSliderChange={onSliderChange}
                                unlockTotals={unlockTotals} showAutoFilled={showAutoFilled} />
                            ))}
                    </div>
                </div>
            </div>
        </form>
    );
}