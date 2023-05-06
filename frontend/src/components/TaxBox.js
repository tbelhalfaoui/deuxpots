export const TaxBox = ({box}) => (
    <div class="row">
    <div class="col-1">
    <input type="text" class="form-control" name={box.code} defaultValue={box.ratio_0} />
    </div>
    <div class="col-2">
    <input type="range" class="form-range" id="customRange1" min="0" max="1" step="0.1" defaultValue={box.ratio_0} />
    </div>
    <div class="col-1">
    <input type="text" class="form-control" name={box.code} defaultValue={box.ratio_0} />
    </div>
    <div class="col">
    <label for={box.code} class="form-label">{box.code} - {box.description}</label>
    </div>
    </div>
)