export const ResultRow = ({ label, fieldName, partnerIndex, style, results }) => (
    <div class="py-1 row" style={style}>
        <div class="col-lg-8">
            {label}&nbsp;:
        </div>
        <div class="col-lg-4 text-end">
            <strong>{ Math.round(results.partners[partnerIndex][fieldName]).toLocaleString('fr-FR') }&nbsp;€</strong>
        </div>
    </div>
);

export const ResultCard = ({ results, partnerIndex }) =>
    results && (
        <div class="card">
            <div class="card-header">
                Déclarant·e {partnerIndex + 1}
            </div>
            <div class="card-body">
                <ResultRow label="Impôt si déclaration séparée" fieldName="tax_if_single" partnerIndex={partnerIndex} results={results} style={{color: 'gray'}} />
                <ResultRow label="Impôt commun individualisé" fieldName="total_tax" partnerIndex={partnerIndex} results={results} style={{}} />
                <ResultRow label="Déjà payé" fieldName="already_paid" partnerIndex={partnerIndex} results={results} style={{color: 'gray'}} />
                {(results.partners[partnerIndex].remains_to_pay && results.partners[1 - partnerIndex].remains_to_pay) &&
                    (<ResultRow label="Reste à payer" fieldName="remains_to_pay" partnerIndex={partnerIndex}
                    results={results} style={{'font-size': '1.5em'}} />)}
                {(results.partners[partnerIndex].remains_to_pay && results.partners[1 - partnerIndex].remains_to_get_back) &&
                    (<ResultRow label="Reste à payer aux impôts" fieldName="remains_to_pay" partnerIndex={partnerIndex}
                    results={results} style={{'font-size': '1.5em'}} />)}
                {(results.partners[partnerIndex].remains_to_get_back && results.partners[1 - partnerIndex].remains_to_pay) &&
                    (<ResultRow label="Reste à récupérer auprès de l'autre co-déclarant·e" fieldName="remains_to_get_back" partnerIndex={partnerIndex}
                    results={results} style={{'font-size': '1.5em'}} />)}
                 {(results.partners[partnerIndex].remains_to_get_back && results.partners[1 - partnerIndex].remains_to_get_back) &&
                    (<ResultRow label="Reste à récupérer" fieldName="remains_to_get_back" partnerIndex={partnerIndex} 
                    results={results} style={{'font-size': '1.5em'}} />)}
            </div>
        </div>
    )

export const ResultsPanel = ({ results }) => (
    <div>
        <div class="row justify-content-center">
            <div class="p-3 col-md-6 col-xl-5">
                <ResultCard results={results} partnerIndex={0} />
            </div>
            <div class="p-3 col-md-6 col-xl-5">
                <ResultCard results={results} partnerIndex={1} />
            </div>
        </div>
    </div>
)
