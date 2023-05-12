export const ResultCard = ({ results, partnerIndex }) => results && (
    <div class="card">
        <div class="card-header">
            Déclarant·e {partnerIndex + 1}
        </div>
        <div class="card-body">
            <p class="card-text" style={{color: 'gray'}}>Impôt si déclaration séparée&nbsp;: <strong>{ Math.round(results.partners[partnerIndex].tax_if_single).toLocaleString('fr-FR') }&nbsp;€</strong></p>
            <p class="card-text">Impôt commun individualisé&nbsp;: <strong>{ Math.round(results.partners[partnerIndex].total_tax).toLocaleString('fr-FR') }&nbsp;€</strong></p>
            <p class="card-text" style={{color: 'gray'}}>Déjà payé&nbsp;: <strong>{ Math.round(results.partners[partnerIndex].already_paid).toLocaleString('fr-FR') }&nbsp;€</strong></p>
            {(results.partners[partnerIndex].remains_to_pay >= 0) && (
                <h5 class="card-title">Reste à payer&nbsp;: <strong>{ Math.round(results.partners[partnerIndex].remains_to_pay).toLocaleString('fr-FR') }&nbsp;€</strong></h5>
            )}
            {(results.partners[partnerIndex].remains_to_pay < 0) && (
                <h5 class="card-title">Reste à récupérer&nbsp;: <strong>{ Math.round(- results.partners[partnerIndex].remains_to_pay).toLocaleString('fr-FR') }&nbsp;€</strong></h5>
            )}
        </div>
    </div>
);

export const ResultsPanel = ({ results }) => (
    <div>
        <div class="row justify-content-center">
            <div class="p-3 col-xl-4">
                <ResultCard results={results} partnerIndex={0} />
            </div>
            <div class="p-3 col-xl-4">
                <ResultCard results={results} partnerIndex={1} />
            </div>
        </div>
    </div>
)
