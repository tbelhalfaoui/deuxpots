import { NumericFormat } from "react-number-format";
import { FaLock, FaLockOpen, FaRegTrashAlt } from "react-icons/fa";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import { BoxSearchSelect } from "./BoxSearchSelect";


const fillNaN = (val) => isNaN(val) ? "" : val

export const NumberBox = ({ max, value, invalidValue, name, label, allow_float, ...props }) => {
    const isAllowed = (val) => {
        var isValid = true
        if (max) {
            isValid &&= (val.floatValue <= max) 
        }
        if (allow_float) {
            isValid &&= (val.floatValue * 10) % 5 === 0
        }
        return isValid || (val.value === "")
    }

    return <div className="form-floating">
        <NumericFormat
            className="form-control box text-center text-lg-end"
            thousandSeparator=" "
            decimalScale={allow_float ? 1 : 0}
            isAllowed={isAllowed}
            defaultValue=""
            min={0}
            max={max}
            name={name}
            value={value}
            placeholder={label}
            style={(invalidValue(value)) ? {backgroundColor: 'rgb(255, 204, 203)'} : {}}
            {...props} />
        <label htmlFor={name}>{label}</label>
    </div>
}

export const BooleanBox = ({ name, label, value, invalidValue, ...props }) =>
    <div className="row form-check form-switch">
        <div className="col-12">
            <input className="form-check-input" type="checkbox" name={name} checked={value}
            style={(invalidValue(value)) ? {backgroundColor: 'rgb(255, 204, 203)'} : {}} { ...props } />
        </div>
        <div className="col-12">
            <label className="form-check-label" htmlFor={name}>{label}</label>
        </div>
    </div>


export const DeleteBoxModal = ({ boxDescription, doDeleteBox, modalId }) =>
    <div className="modal modal-lg fade" id={modalId} tabIndex="-1" aria-labelledby={`${modalId}Label`} aria-hidden="true">
        <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
            <div className="modal-content">
                <div className="modal-header">
                    <h5 className="modal-title" id={`${modalId}Label`}>Voulez-vous supprimer cette ligne ?</h5>
                    <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div className="modal-body text-start">
                    {boxDescription}
                </div>
                <div className="modal-footer">
                    <button type="button" className="btn btn-danger" data-bs-dismiss="modal" onClick={doDeleteBox}>Supprimer</button>
                    <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Conserver</button>
                </div>
            </div>
        </div>
    </div>


export const TaxBox = ({ boxIndex, box, onNumericValueChange, onBooleanValueChange, onSliderChange,
                         deleteBox, toggleTotalLock, reassignBox }) => (
    <div>
        <div className="row">
            <div className="d-flex align-items-center align-items-stretch col-md-6 pe-lg-4 pe-xxl-4">
                <div className="d-flex flex-fill align-items-center row">
                    <div className="col-10 col-xxl-11">
                        <BoxSearchSelect box={box} boxIndex={boxIndex} reassignBox={reassignBox} />
                    </div>
                    <div className="col-2 col-xxl-1">
                        <div className="d-flex row align-items-center">
                            <div className="col-12 col-lg-6">
                                <OverlayTrigger placement="left" overlay={
                                    <Tooltip id="tooltipTrash">
                                        Supprimer cette ligne.
                                    </Tooltip>
                                }>
                                    <button className="btn btn-link p-0 m-0" type="button" data-bs-toggle="modal" data-bs-target={`#deleteBoxModal${boxIndex}`}
                                    disabled={!box.code}>
                                        <FaRegTrashAlt style={{color: 'dimGray'}} />
                                    </button>
                                </OverlayTrigger>
                                <DeleteBoxModal boxDescription={`${box.code} - ${box.description}`} doDeleteBox={() => deleteBox(boxIndex)}
                                modalId={`deleteBoxModal${boxIndex}`} />
                            </div>
                            <div className="col-12 col-lg-6">
                                {(box.type !== "bool") && 
                                    <OverlayTrigger placement="left" overlay={
                                        <Tooltip id="tooltipLock">
                                            {box.totalIsLocked ? "Déverrouiller le total (modifier les deux déclarant·e·s séparement)."
                                                                : "Verrouiller le total (ajuster la répartition entre les deux déclarant·e·s)."}
                                        </Tooltip>
                                    }>
                                        <button className="btn btn-link p-0 m-0" type="button" onClick={() => toggleTotalLock(boxIndex, !box.totalIsLocked)}
                                        disabled={!box.raw_value}>
                                            {box.totalIsLocked ?
                                            (<FaLock style={{color: 'dimGray'}} />) :
                                            (<FaLockOpen style={{color: 'dimGray'}} />)}
                                        </button>
                                    </OverlayTrigger>}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="d-flex align-items-center col-md-6">
                <div className="flex-fill row">
                    <div className="p-1 col-lg-3">
                        {(box.type !== "bool") && 
                            <NumberBox name={`raw_value.${boxIndex}`} value={box.raw_value} label="Total"
                            onValueChange={onNumericValueChange} disabled invalidValue={(val) => parseInt(val) !== val} />}
                    </div>
                    <div className="d-flex align-items-center justify-content-center p-1 col-4 col-lg-3">
                        {(box.type === "bool") ?
                            <BooleanBox name={`partner_0_value.${boxIndex}`} value={box.partner_0_value}
                            invalidValue={(val) => !val && val !== 0 && box.code} label="Décl. 1" onChange={onBooleanValueChange} />
                          : <NumberBox name={`partner_0_value.${boxIndex}`} value={fillNaN(box.partner_0_value)} label="Décl. 1"
                            max={box.totalIsLocked ? box.raw_value : undefined} onValueChange={onNumericValueChange}
                            invalidValue={(val) => !val && val !== 0 && box.code}
                            allow_float={box.type === "float"} disabled={!box.code} /> 
                        }
                    </div>
                    <div className="d-flex align-items-center p-1 col-4 col-lg-3">
                        {(box.type !== "bool") && 
                            <input type="range" className="form-range" name={`slider.${boxIndex}`}
                            min={0} max={box.raw_value}
                            step={(box.type === "float") ? 0.5 : (box.raw_value <= 10) ? 1 : parseInt(box.raw_value / 10)}
                            disabled={(!box.raw_value) || (!box.code)}
                            value={fillNaN(box.attribution * box.raw_value)}
                            onChange={onSliderChange} />}
                    </div>
                    <div className="d-flex align-items-center justify-content-center p-1 col-4 col-lg-3">
                        <div className="form-floating">
                            {(box.type === "bool") ?
                                <BooleanBox name={`partner_1_value.${boxIndex}`} value={box.partner_1_value}
                                invalidValue={(val) => !val && val !== 0 && box.code} label="Décl. 2" onChange={onBooleanValueChange} />
                              : <NumberBox name={`partner_1_value.${boxIndex}`} value={fillNaN(box.partner_1_value)} label="Décl. 2"
                                max={box.totalIsLocked ? box.raw_value : undefined} onValueChange={onNumericValueChange}
                                invalidValue={(val) => !val && val !== 0 && box.code}
                                allow_float={box.type === "float"} disabled={!box.code} />
                            }
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div className="py-2 py-lg-0">
            <hr/>
        </div>
    </div>
);