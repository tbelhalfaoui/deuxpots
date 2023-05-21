import { NumericFormat } from "react-number-format";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrashCan } from "@fortawesome/free-regular-svg-icons";
import { faLink, faLinkSlash } from "@fortawesome/free-solid-svg-icons";

// import SelectSearch from 'react-select-search';
// import Combobox from "react-widgets/Combobox";


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

export const TaxBox = ({boxIndex, box, onValueChange, onSliderChange, showAutoFilled, toggleBoxEdit, deleteBox, toggleTotalLock}) => {
    // const options = [
    //     {name: 'Swedish', value: 'sv'},
    //     {name: 'English', value: 'en'},
    //     {
    //         type: 'group',
    //         name: 'Group name',
    //         items: [
    //             {name: 'Spanish', value: 'es'},
    //         ]
    //     },
    // ];

    return ((box.original_attribution == null) || (showAutoFilled)) && (
    <div>
        <div className="row">
            <div className="d-flex align-items-center align-items-stretch col-md-6">
                <div className="d-flex flex-fill align-items-center row">
                    <div className="col-10 col-xl-11">
                        {(box.isBeingEdited && false) ?
                            <textarea className="form-control" rows="2" data-bs-toggle="dropdown"
                            placeholder="Saisissez le code ou le nom de la case à ajouter." value={`${box.code} - ${box.description}`}
                            onBlur={() => toggleBoxEdit(boxIndex, false)} autoFocus />
                            : <label htmlFor={`raw_value.${boxIndex}`} className="form-label" onClick={() => toggleBoxEdit(boxIndex, true)}>
                                {box.code} - {box.description}
                            </label>
                        }
                    </div>
                    {false && <div className="col-1 col-xl-1">
                        <button className="btn" style={{color: 'red'}} type="button" onClick={() => deleteBox(boxIndex)}>
                            <FontAwesomeIcon icon={faTrashCan} />
                        </button>
                    </div>}
                    <div className="col-1 col-xl-1">
                        <button className="btn" type="button" onClick={() => toggleTotalLock(boxIndex, !box.totalIsLocked)}>
                            {box.totalIsLocked ?
                            (<FontAwesomeIcon style={{color: 'gray'}} icon={faLink} />) :
                            (<FontAwesomeIcon icon={faLinkSlash} />)}
                        </button>
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
)}