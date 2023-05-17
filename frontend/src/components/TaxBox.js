import { NumericFormat } from "react-number-format";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrashCan } from "@fortawesome/free-regular-svg-icons";


export const NumberBox = ( props ) => (
    <NumericFormat
        class={`form-control box text-center text-lg-end ${((!props.value) && (props.value !== 0)) && 'invalidBox'}`}
        thousandSeparator=" "
        decimalScale={0}
        isAllowed={(val) => (props.max) ? ((val.floatValue <= props.max) || (val.value === "")) : true}
        defaultValue=""
        {...props} />
)

export const TaxBox = ({box, onValueChange, onSliderChange, unlockTotals, showAutoFilled, deleteItem}) => 
    ((box.original_attribution == null) || (showAutoFilled)) && (
    <div>
        <div class="row">
            <div class="d-flex align-items-center align-items-stretch col-md-6">
                <div class="d-flex flex-fill align-items-center row">
                    <div class="col-10 col-xl-11">
                        <label for={`${box.code}.raw_value`} class="form-label">{box.code} - {box.description}</label>
                    </div>
                    <div class="col-1 col-xl-1">
                        <button class="btn btn-link" style={{color: 'red'}} type="button" onClick={() => deleteItem(box.code)}>
                            <FontAwesomeIcon icon={faTrashCan} />
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6 d-flex align-items-center">
                <div class="row">
                    <div class="p-1 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`${box.code}.raw_value`} value={box.raw_value} placeholder="Total"
                            onValueChange={onValueChange} disabled={true} />
                            <label for={`${box.code}.raw_value`}>Total</label>
                        </div>
                    </div>
                    <div class="p-1 col-4 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`${box.code}.partner_0_value`} value={box.partner_0_value} placeholder="Décl. 1"
                            max={!unlockTotals && box.raw_value} onValueChange={onValueChange} />
                            <label for={`${box.code}.partner_0_value`}>Décl. 1</label>
                        </div>
                    </div>
                    <div class="d-flex align-items-center p-1 col-4 col-lg-3">
                        <input type="range" class="form-range" name={`${box.code}.slider`}
                        min="0" max={box.raw_value}
                        step={(box.raw_value <= 10) ? 1 : parseInt(box.raw_value / 10)}
                        disabled={box.raw_value === ""}
                        value={(!box.partner_0_value && !box.partner_1_value) ? "" : box.attribution * box.raw_value}
                        onChange={onSliderChange} />
                    </div>
                    <div class="p-1 col-4 col-lg-3">
                        <div class="form-floating">
                            <NumberBox name={`${box.code}.partner_1_value`} value={box.partner_1_value} placeholder="Décl. 2"
                            max={!unlockTotals && box.raw_value} onValueChange={onValueChange} />
                            <label for={`${box.code}.partner_1_value`}>Décl. 2</label>
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