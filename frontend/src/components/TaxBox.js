import { NumericFormat } from "react-number-format";


export const NumberBox = ( props ) => (
    <NumericFormat class="form-control"
        thousandSeparator=" "
        decimalScale={0}
        isAllowed={(val) => (props.max) ? ((val.floatValue <= props.max) || (val.value == "")) : true}
        defaultValue=""
        {...props} />
)

export const TaxBox = ({box, onValueChange, onSliderChange, unlockTotals, showAutoFilled}) => 
    ((box.original_ratio == null) || (showAutoFilled)) && (
    <div class="row">
        <div class="col-1">
            <NumberBox name={`${box.code}.raw_value`} value={box.raw_value} onValueChange={onValueChange} disabled={!unlockTotals} />
        </div>
        <div class="col-1">
            <NumberBox name={`${box.code}.partner_0_value`} value={box.partner_0_value} max={box.raw_value} onValueChange={onValueChange}
            style={(box.partner_0_value == null) ? {'background-color': 'rgb(255, 240, 189)'} : {}} />
        </div>
        <div class="col-2">
            <input type="range" class="form-range" name={`${box.code}.slider`}
            min="0" max={box.raw_value}
            step={(box.raw_value <= 10) ? 1 : parseInt(box.raw_value / 10)}
            disabled={box.raw_value == ""}
            value={(box.raw_value != "") ? (1 - box.ratio) * box.raw_value : ""}
            onChange={onSliderChange} />
        </div>
        <div class="col-1">
            <NumberBox name={`${box.code}.partner_1_value`} value={box.partner_1_value} max={box.raw_value} onValueChange={onValueChange}
            style={(box.partner_1_value == null) ? {'background-color': 'rgb(255, 240, 189)'} : {}} />
        </div>
        <div class="col">
            <label for={`${box.code}.raw_value`} class="form-label">{box.code} - {box.description}</label>
        </div>
    </div>
)