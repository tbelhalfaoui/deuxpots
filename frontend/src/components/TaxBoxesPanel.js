import React, { useState, useContext } from "react"
import { FaInfoCircle } from "react-icons/fa";
import { NavContext, SearchIndexContext } from "../App.js";
import { TaxBox } from './TaxBox.js'
import { SubmitButton } from './SubmitButton.js'
import { ErrorMessage, WarningMessage } from "./Alert.js";
import { callIndividualizeRoute } from "../adapters/api.js"
import { createEmptyBox } from "../utils/box.js";


const round = (val, precision) => Math.round(val / precision) * precision

export const TaxBoxesPanel = ({ boxes, setBoxes, setIndividualizedResults,
                                warnings, errorMsg, setErrorMsg, resetErrorMsgs, isDemo }) => {
    const [ isLoading, setIsLoading ] = useState(false);
    const { setStep } = useContext(NavContext);
    const searchIndex = useContext(SearchIndexContext);

    const handleSliderChange = async (evt) => {
        var value = evt.target.value;
        const boxIndexChanged = parseInt(evt.target.name.split('.')[1]);
        
        setBoxes(boxes.map((box, boxIndex) => {
            if (boxIndex === boxIndexChanged) {
                const precision = (box.type === "float") ? .1 : 1
                box.attribution = value / box.raw_value
                box.partner_0_value = round((1 - box.attribution) * box.raw_value, precision)
                box.partner_1_value = round(box.attribution * box.raw_value, precision)
            }
            return box;
        }));
    }
    
    const handleNumericBoxChange = async (values, sourceInfo) => {
        const evt = sourceInfo.event;
        if (!evt) {
            return;
        }
        const fieldName = evt.target.name.split('.')[0];
        const boxIndexChanged = parseInt(evt.target.name.split('.')[1]);

        setBoxes(boxes.map((box, boxIndex) => {
            if (boxIndex === boxIndexChanged) {
                const precision = (box.type === "float") ? .1 : 1
                box[fieldName] = values.floatValue;
                if (!box.totalIsLocked) {
                    box.raw_value = (box.partner_0_value || 0) + (box.partner_1_value || 0)
                }
                else if (fieldName === 'partner_0_value') {
                    box.partner_1_value = round(box.raw_value - box.partner_0_value, precision)
                }
                else if (fieldName === 'partner_1_value') {
                    box.partner_0_value = round(box.raw_value - box.partner_1_value, precision)
                }
                if (box.raw_value) {
                    box.attribution = box.partner_1_value / box.raw_value
                }
            }
            return box;
        }))
    };

    const handleBooleanBoxChange = async (evt) =>{
        const fieldName = evt.target.name.split('.')[0];
        const boxIndexChanged = parseInt(evt.target.name.split('.')[1]);

        setBoxes(boxes.map((box, boxIndex) => {
            if (boxIndex === boxIndexChanged) {
                box[fieldName] = evt.target.checked * 1;
                box.raw_value = (box.partner_0_value || 0) + (box.partner_1_value || 0);
            }
            return box;
        }))
    }

    const toggleTotalLock = (boxIndexChanged, totalIsLocked) => {
        setBoxes(boxes.map(
            (box, boxIndex) => 
                (boxIndex === boxIndexChanged) ? {
                ...box,
                totalIsLocked: totalIsLocked
            } : box
        ));
    }

    const reassignBox = (boxIndexChanged, newCode, newDescription, newType) => {
        const oldCode = boxes[boxIndexChanged].code;
        if (newCode !== oldCode) {
            setBoxes(boxes.map(
                (box, boxIndex) => 
                    (boxIndex === boxIndexChanged) ? {
                        ...box,
                        code: newCode,
                        description: newDescription,
                        type: newType,
                        totalIsLocked: false,
                        partner_0_value: "",
                        partner_1_value: "",
                    } : box
            ).concat((oldCode) ? [] : [createEmptyBox()]));
        }
        searchIndex.current.disable(newCode)
        if (oldCode) {
            searchIndex.current.reEnable(oldCode)
        }
    }

    const deleteBox = (boxIndexChanged) =>
        setBoxes(boxes.filter((box, boxIndex) => {
            const hasBeenDeleted = boxIndex === boxIndexChanged
            if (hasBeenDeleted) {
                searchIndex.current.reEnable(box.code)
            }
            return !hasBeenDeleted
        }))

    const fetchIndividualizedResults = async (evt) => {
        evt.preventDefault();
        const nonEmptyBoxes = boxes.filter(
            box => box.code
        );
        const allBoxesAreFilled = nonEmptyBoxes.flatMap(
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

        await callIndividualizeRoute(
            nonEmptyBoxes, isDemo
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
                setStep({current: 3, max: 3})
            }
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
                {isDemo ?
                    <div className="alert alert-primary" role="alert">
                        <FaInfoCircle /> Les données ci-dessous sont un exemple.<br/>
                        Vous pouvez cliquer sur chaque intitulé pour le modifier,
                        ajouter une nouvelle ligne en bas de la liste et modifier les différents montants.
                    </div>
                :   <div className="alert alert-primary" role="alert">
                        <FaInfoCircle /> Les données suivantes ont été extraites de votre déclaration
                        de revenus. Merci de vérifier qu'elles sont correctes.<br/>
                        Les cases en rouge sont à compléter en indiquant la répartition entre les déclarant·e·s.
                    </div>
                }
                <div>
                    <div>
                        <div className="py-0">
                            <hr/>
                        </div>
                        {boxes.map((box, boxIndex) => (
                            <TaxBox key={boxIndex}
                             boxIndex={boxIndex} box={box}
                             onNumericValueChange={handleNumericBoxChange}
                             onBooleanValueChange={handleBooleanBoxChange}
                             onSliderChange={handleSliderChange}
                             deleteBox={deleteBox}
                             toggleTotalLock={toggleTotalLock}
                             reassignBox={reassignBox} />
                        ))}
                    </div>
                </div>
                <ErrorMessage error={errorMsg} />
                <SubmitButton isLoading={isLoading} />
            </div>
        </form>
    );
}