import { NumericFormat } from "react-number-format";


export const TaxBox = ({box, onChange, modifyTotals}) => (
    <div class="row">
        <div class="col-1">
            <NumericFormat class="form-control" name={`${box.code}.raw_value`} value={box.raw_value}
            thousandSeparator=" " disabled={!modifyTotals} onChange={onChange} />
        </div>
        <div class="col-1">
            <NumericFormat class="form-control" name={`${box.code}.partner_0_value`} value={box.partner_0_value}
            thousandSeparator=" " onChange={onChange} min="0" max={box.raw_value}/>
        </div>
        <div class="col-2">
            <input type="range" class="form-range" name={`${box.code}.slider`}
            min="0" max={box.raw_value}
            step={(box.raw_value <= 10) ? 1 : Math.round(box.raw_value / 10)}
            disabled={box.raw_value == ""}
            value={(box.raw_value != "") ? (1 - box.ratio_0) * box.raw_value : ""}
            onChange={onChange} />
        </div>
        <div class="col-1">
            <NumericFormat min="0" max={box.raw_value} class="form-control" 
            thousandSeparator=" " name={`${box.code}.partner_1_value`} value={box.partner_1_value} onChange={onChange} />
        </div>
        <div class="col">
            <label for={`${box.code}.raw_value`} class="form-label">{box.code} - {box.description}</label>
        </div>
    </div>
)