import { TaxBox } from './TaxBox.js'

export const TaxBoxesPanel = ({boxes}) => (
    <form>
        <div id="containerStep2">
        {boxes.length > 0 && (
            <div class="container py-2 text-start">
            <div class="accordion" id="accordionBoxes">
                <div class="accordion-item">
                <h2 class="accordion-header" id="headingManualBoxes">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseManualBoxes" aria-expanded="true" aria-controls="collapseManualBoxes">
                    Cases communes, à attribuer manuellement.
                    </button>
                </h2>
                <div id="collapseManualBoxes" class="accordion-collapse collapse show" aria-labelledby="headingManualBoxes" data-bs-parent="#accordionBoxes">
                    <div class="accordion-body">
                    {boxes.filter(
                    box => box.ratio_0 == null
                    ).map(box => (
                    <TaxBox box={box} />
                    ))}
                    </div>
                </div>
                </div>
                <div class="accordion-item">
                <h2 class="accordion-header" id="headingAutoBoxes">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseAutoBoxes" aria-expanded="false" aria-controls="collapseAutoBoxes">
                    Cases séparées, attribuées automatiquement.
                    </button>
                </h2>
                <div id="collapseAutoBoxes" class="accordion-collapse collapse" aria-labelledby="headingAutoBoxes" data-bs-parent="#accordionBoxes">
                    <div class="accordion-body">
                    {boxes.filter(
                    box => box.ratio_0 != null
                    ).map(box => (
                    <TaxBox box={box} />
                    ))}
                    </div>
                </div>
                </div>
            </div>
            </div>
        )}
        </div>
    </form>
)