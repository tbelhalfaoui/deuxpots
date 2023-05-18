import { NumericFormat } from "react-number-format";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrashCan } from "@fortawesome/free-regular-svg-icons";
import SelectSearch from 'react-select-search';


export const NumberBox = ( props ) => (
    <NumericFormat
        class={`form-control box text-center text-lg-end ${((!props.value) && (props.value !== 0)) && 'invalidBox'}`}
        thousandSeparator=" "
        decimalScale={0}
        isAllowed={(val) => (props.max) ? ((val.floatValue <= props.max) || (val.value === "")) : true}
        defaultValue=""
        {...props} />
)

export const TaxBox = ({boxIndex, box, onValueChange, onSliderChange, unlockTotals, showAutoFilled, toggleBoxEdit, deleteBox}) => 
    ((box.original_attribution == null) || (showAutoFilled)) && (
    <div>
        <div class="row">
            <div class="d-flex align-items-center align-items-stretch col-md-6">
                <div class="d-flex flex-fill align-items-center row">
                    <div class="col-10 col-xl-11">
                        {(box.isBeingEdited) ?
                            <textarea class="form-control" rows="2" placeholder="Saisissez le code ou le nom de la case à ajouter."
                            value={`${box.code} - ${box.description}`} onBlur={() => toggleBoxEdit(boxIndex, false)} autoFocus />
                            : <label for={`raw_value.${boxIndex}`} class="form-label" onClick={() => toggleBoxEdit(boxIndex, true)}>
                                {box.code} - {box.description}
                            </label>
                        }
                    </div>
                    <div class="col-1 col-xl-1">
                        <button class="btn" style={{color: 'red'}} type="button" onClick={() => deleteBox(boxIndex)}>
                            <FontAwesomeIcon icon={faTrashCan} />
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6 d-flex align-items-center">
                <div class="row">
                    <div class="p-1 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`raw_value.${boxIndex}`} value={box.raw_value} placeholder="Total"
                            onValueChange={onValueChange} disabled={true} />
                            <label for={`raw_value.${boxIndex}`}>Total</label>
                        </div>
                    </div>
                    <div class="p-1 col-4 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`partner_0_value.${boxIndex}`} value={box.partner_0_value} placeholder="Décl. 1"
                            max={!unlockTotals && box.raw_value} onValueChange={onValueChange} />
                            <label for={`partner_0_value.${boxIndex}`}>Décl. 1</label>
                        </div>
                    </div>
                    <div class="d-flex align-items-center p-1 col-4 col-lg-3">
                        <input type="range" class="form-range" name={`slider.${boxIndex}`}
                        min="0" max={box.raw_value}
                        step={(box.raw_value <= 10) ? 1 : parseInt(box.raw_value / 10)}
                        disabled={box.raw_value === ""}
                        value={(!box.partner_0_value && !box.partner_1_value) ? "" : box.attribution * box.raw_value}
                        onChange={onSliderChange} />
                    </div>
                    <div class="p-1 col-4 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`partner_1_value.${boxIndex}`} value={box.partner_1_value} placeholder="Décl. 2"
                            max={!unlockTotals && box.raw_value} onValueChange={onValueChange} />
                            <label for={`partner_1_value.${boxIndex}`}>Décl. 2</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="py-2 py-lg-0">
            <hr/>
        </div>
    </div>
)