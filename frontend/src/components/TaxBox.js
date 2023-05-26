import { NumericFormat } from "react-number-format";
import { FaLock, FaLockOpen, FaRegTrashAlt } from "react-icons/fa";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import { BoxSearchSelect } from "./BoxSearchSelect";


export const NumberBox = ( props ) => (
    <NumericFormat
        className="form-control box text-center text-lg-end"
        thousandSeparator=" "
        decimalScale={0}
        isAllowed={(val) => (props.max) ? ((val.floatValue <= props.max) || (val.value === "")) : true}
        defaultValue=""
        min={0}
        style={((!props.value) && (props.value !== 0)) ? {backgroundColor: 'rgb(255, 204, 203)'} : {}}
        {...props} />
)

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


export const TaxBox = ({ boxIndex, box, onValueChange, onSliderChange,
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
                                     <button className="btn p-0 m-0" type="button" data-bs-toggle="modal" data-bs-target={`#deleteBoxModal${boxIndex}`}>
                                        <FaRegTrashAlt style={{color: 'gray'}} />
                                    </button>
                                </OverlayTrigger>
                                <DeleteBoxModal boxDescription={`${box.code} - ${box.description}`} doDeleteBox={() => deleteBox(boxIndex)}
                                modalId={`deleteBoxModal${boxIndex}`} />
                            </div>
                            <div className="col-12 col-lg-6">
                                <OverlayTrigger placement="left" overlay={
                                    <Tooltip id="tooltipLock">
                                        {box.totalIsLocked ? "Déverrouiller le total (modifier les deux déclarant·e·s séparement)."
                                                            : "Verrouiller le total (ajuster la répartition entre les deux déclarant·e·s)."}
                                    </Tooltip>
                                }>
                                    <button className="btn p-0 m-0" type="button" onClick={() => toggleTotalLock(boxIndex, !box.totalIsLocked)}>
                                        {box.totalIsLocked ?
                                        (<FaLock style={{color: 'gray'}} />) :
                                        (<FaLockOpen />)}
                                    </button>
                                </OverlayTrigger>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="col-md-6 d-flex align-items-center">
                <div className="row">
                    <div className="p-1 col-lg-3">
                        <div className="form-floating">
                            <NumberBox name={`raw_value.${boxIndex}`} value={box.raw_value} placeholder="Total"
                            onValueChange={onValueChange} disabled={true} />
                            <label htmlFor={`raw_value.${boxIndex}`}>Total</label>
                        </div>
                    </div>
                    <div className="p-1 col-4 col-lg-3">
                        <div className="form-floating">
                            <NumberBox name={`partner_0_value.${boxIndex}`} value={box.partner_0_value} placeholder="Décl. 1"
                            max={box.totalIsLocked ? box.raw_value : undefined} onValueChange={onValueChange} />
                            <label htmlFor={`partner_0_value.${boxIndex}`}>Décl. 1</label>
                        </div>
                    </div>
                    <div className="d-flex align-items-center p-1 col-4 col-lg-3">
                        <input type="range" className="form-range" name={`slider.${boxIndex}`}
                        min={0} max={box.raw_value}
                        step={(box.raw_value <= 10) ? 1 : parseInt(box.raw_value / 10)}
                        disabled={box.raw_value === ""}
                        value={(!box.partner_0_value && !box.partner_1_value) ? "" : box.attribution * box.raw_value}
                        onChange={onSliderChange} />
                    </div>
                    <div className="p-1 col-4 col-lg-3">
                        <div className="form-floating">
                            <NumberBox name={`partner_1_value.${boxIndex}`} value={box.partner_1_value} placeholder="Décl. 2"
                            max={box.totalIsLocked ? box.raw_value : undefined} onValueChange={onValueChange} />
                            <label htmlFor={`partner_1_value.${boxIndex}`}>Décl. 2</label>
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