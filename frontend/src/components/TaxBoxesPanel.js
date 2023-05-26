import { useState } from "react"
import { FaInfoCircle } from "react-icons/fa";
import { TaxBox } from './TaxBox.js'
import { SubmitButton } from './SubmitButton.js'
import { ErrorMessage, WarningMessage } from "./Alert.js";


export const TaxBoxesPanel = ({ boxes, setBoxes, setStep, setIndividualizedResults,
                                warnings, errorMsg, setErrorMsg, resetErrorMsgs, isDemo }) => {
    const [ isLoading, setIsLoading ] = useState(false);

    const onSliderChange = async (evt) => {
        var value = evt.target.value;
        const boxIndexChanged = parseInt(evt.target.name.split('.')[1]);
        if (isNaN(value)) {
            value = "";
        }

        setBoxes(boxes.map((box, boxIndex) => {
            if (boxIndex === boxIndexChanged) {
                box.attribution = value / box.raw_value;
                box.partner_0_value = Math.round((1 - box.attribution) * box.raw_value);
                box.partner_1_value = Math.round(box.attribution * box.raw_value);
            }
            return box;
        }));
    }

    const handleBoxChange = async (boxIndexChanged, fieldName, value) =>
        setBoxes(boxes.map((box, boxIndex) => {
            if (boxIndex === boxIndexChanged) {
                box[fieldName] = value;
                if (!box.totalIsLocked) {
                    box.raw_value = Math.round((box.partner_0_value || 0) + (box.partner_1_value || 0));
                }
                else if (fieldName === 'partner_0_value') {
                    box.partner_1_value = Math.round(box.raw_value - box.partner_0_value);
                }
                else if (fieldName === 'partner_1_value') {
                    box.partner_0_value = Math.round(box.raw_value - box.partner_1_value);
                }
                if (box.raw_value) {
                    box.attribution = box.partner_1_value / box.raw_value;
                }
            }
            return box;
        }));

    const onBoxChange = async (values, sourceInfo) => {
        const evt = sourceInfo.event;
        if (!evt) {
            return;
        }
        const fieldName = evt.target.name.split('.')[0];
        const boxIndex = parseInt(evt.target.name.split('.')[1]);
        handleBoxChange(boxIndex, fieldName, values.floatValue)
    };

    const toggleBoxEdit = (boxIndexChanged, isBeingEdited) => {
        setBoxes(boxes.map(
            (box, boxIndex) => 
                (boxIndex === boxIndexChanged) ? {
                ...box,
                isBeingEdited: isBeingEdited
            } : box
        ));
    }

    const toggleTotalLock = (boxIndexChanged, totalIsLocked) => {
        setBoxes(boxes.map(
            (box, boxIndex) => 
                (boxIndex === boxIndexChanged) ? {
                ...box,
                totalIsLocked: box.raw_value ? totalIsLocked : false
            } : box
        ));
    }

    const deleteBox = (boxIndexChanged) => {
        setBoxes(boxes.filter((box, boxIndex) => boxIndex !== boxIndexChanged));
    };

    const addNewBox = () => {
        setBoxes([...boxes, {}]);
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

        resetErrorMsgs();
        setIsLoading(true);

        const queryParams = new URLSearchParams();
        if (isDemo) {
            queryParams.append("demo", "true");
        }
        await fetch(`${process.env.REACT_APP_API_URL || window.location.origin}/individualize?${queryParams}`, {
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
            <div id="containerStep2" className="container py-2 text-start">
                <ErrorMessage error={errorMsg} />
                {warnings.map(msg =>
                    (<WarningMessage key={msg} warning={msg} />)
                )}
                {!boxes &&
                (<div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="sr-only"></span>
                    </div>
                </div>)}
                <div className="alert alert-primary" role="alert">
                    <FaInfoCircle /> Les données suivantes ont été extraites de votre déclaration
                    de revenus. Merci de vérifier qu'elles sont correctes.<br/>
                    Les cases en rouge sont à compléter en indiquant la répartition entre les déclarant·e·s.
                </div>
                <div>
                    <div>
                        <div className="py-0">
                            <hr/>
                        </div>
                        {boxes.map((box, boxIndex) => (
                            <TaxBox key={box.code} boxIndex={boxIndex} box={box} onValueChange={onBoxChange} onSliderChange={onSliderChange}
                            toggleBoxEdit={toggleBoxEdit} deleteBox={deleteBox} toggleTotalLock={toggleTotalLock} />
                        ))}
                    </div>
                </div>
                <ErrorMessage error={errorMsg} />
                <SubmitButton isLoading={isLoading} />
            </div>
        </form>
    );
}