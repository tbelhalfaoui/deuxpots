import { useState } from "react"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-regular-svg-icons";
import { TaxBox } from './TaxBox.js'
import { SubmitButton } from './SubmitButton.js'
import { ErrorMessage } from "./ErrorMessage.js";


export const TaxBoxesPanel = ({ boxes, setBoxes, setStep, setIndividualizedResults }) => {

    const [ showAutoFilled, setShowAutoFilled ] = useState(true);
    const [ unlockTotals, setUnlockTotals ] = useState(false);
    const [ errorMsg, setErrorMsg ] = useState();
    const [ isLoading, setIsLoading ] = useState(false);


    const onSliderChange = async (evt) => {
        var value = evt.target.value;
        const boxCode = evt.target.name.split('.')[0];
        if (isNaN(value)) {
            value = "";
        }
        let boxesNew = { ...boxes };
        boxesNew[boxCode].attribution = value / boxesNew[boxCode].raw_value;
        boxesNew[boxCode]['partner_0_value'] = Math.round((1 - boxesNew[boxCode]['attribution']) * boxesNew[boxCode]['raw_value']);
        boxesNew[boxCode]['partner_1_value'] = Math.round(boxesNew[boxCode]['attribution'] * boxesNew[boxCode]['raw_value']);
        setBoxes(boxesNew);
    }

    const handleBoxChange = async (boxCode, fieldName, value) => {
        let boxesNew = { ...boxes };
        boxesNew[boxCode][fieldName] = value;

        if (unlockTotals) {
            boxesNew[boxCode]['raw_value'] = Math.round((boxesNew[boxCode]['partner_0_value'] || 0) + (boxesNew[boxCode]['partner_1_value'] || 0));
        }
        else if (fieldName === 'partner_0_value') {
            boxesNew[boxCode]['partner_1_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_0_value']);
        }
        else if (fieldName === 'partner_1_value') {
            boxesNew[boxCode]['partner_0_value'] = Math.round(boxesNew[boxCode]['raw_value'] - boxesNew[boxCode]['partner_1_value']);
        }
        boxesNew[boxCode]['attribution'] = boxesNew[boxCode]['partner_1_value'] / boxesNew[boxCode]['raw_value'];
        
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

    const deleteBox = (boxCode) => {
        let boxesNew = { ...boxes };
        delete boxesNew[boxCode];
        setBoxes(boxesNew);
    };

    const addNewBox = () => {
        let boxesNew = { ...boxes };
        boxesNew['new'] = {'code':'new'};
        setBoxes(boxesNew);
    }

    const fetchIndividualizedResults = async (evt) => {
        evt.preventDefault();
        
        const allBoxesAreFilled = Object.values(boxes).flatMap(
            box => [box.raw_value, box.partner_0_value, box.partner_1_value]
        ).every(
            value => value || (value === 0)
        )
        if (!allBoxesAreFilled) {
            setErrorMsg('Toutes les cases en rouge doivent être remplies.')
            return
        }

        setErrorMsg(null);
        setIsLoading(true);

        await fetch(`${process.env.REACT_APP_API_URL}/individualize`, {
            method: "POST",
            body: JSON.stringify({'boxes': Object.values(boxes)}),
            mode: 'cors',
            headers: {
                'Content-type':'application/json', 
                'Accept':'application/json'
            }
        }).then(
            res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
        ).then(
          res => res.json()
        ).then(
            data => {
                const results = data.individualized;
                [0, 1].forEach(partnerIndex => {
                    if (results.partners[partnerIndex].remains_to_pay < 0) {
                        results.partners[partnerIndex].remains_to_get_back = - results.partners[partnerIndex].remains_to_pay
                        results.partners[partnerIndex].remains_to_pay = null
                    }
                })
                setIndividualizedResults(results)
            }
        ).then(
          () => setStep(3)
        ).catch(
            e => setErrorMsg(e)
        ).finally(
            () => setIsLoading(false)
        )
    };
    
    return (
        <form method="POST" onSubmit={fetchIndividualizedResults}>
            <div id="containerStep2" class="container py-2 text-start">
                <ErrorMessage error={errorMsg} />
                {!boxes &&
                (<div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="sr-only"></span>
                    </div>
                </div>)}
                <div>
                    <div>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="row">
                                    <div class="col-lg-6">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" role="switch" id="showAutofilled" checked={showAutoFilled} onChange={toggleShowAutofilled} />
                                            <label class="form-check-label" for="showAutofilled">Afficher les cases préremplies.</label>
                                        </div>
                                    </div>
                                    <div class="col-lg-6">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" role="switch" id="unlockTotals" checked={unlockTotals} onChange={toggleUnlockTotals} />
                                            <label class="form-check-label" for="unlockTotals">Déverrouiller les totaux.</label>
                                        </div>  
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-center justify-content-md-end pt-3 pt-md-0 col-md-4">
                                <button class="align-self-center btn btn-sm btn-outline-primary" type="button" onClick={addNewBox}>
                                    <FontAwesomeIcon icon={faSquarePlus} /> Ajouter une ligne
                                </button>
                            </div>
                        </div>
                        <div class="py-2">
                            <hr/>
                        </div>
                        {Object.values(boxes).map(box => (
                            <TaxBox box={box} onValueChange={onBoxChange} onSliderChange={onSliderChange}
                            unlockTotals={unlockTotals} showAutoFilled={showAutoFilled} deleteBox={deleteBox} />
                        ))}
                    </div>
                </div>
                <ErrorMessage error={errorMsg} />
                <SubmitButton isLoading={isLoading} />
            </div>
        </form>
    );
}