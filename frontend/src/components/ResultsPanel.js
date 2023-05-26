import Plot from 'react-plotly.js';


export const ResultRow = ({ label, fieldName, partnerIndex, style, results }) => (
    <div className="py-1 row" style={style}>
        <div className="col-lg-8">
            {label}&nbsp;:
        </div>
        <div className="col-lg-4 text-end">
            <strong>{ Math.round(results.partners[partnerIndex][fieldName]).toLocaleString('fr-FR') }&nbsp;€</strong>
        </div>
    </div>
);

export const ResultCard = ({ results, partnerIndex }) =>
    results && (
        <div className="card">
            <div className="card-header">
                Déclarant·e {partnerIndex + 1}
            </div>
            <div className="card-body">
                <ResultRow label="Impôt si déclaration séparée" fieldName="tax_if_single" partnerIndex={partnerIndex} results={results} style={{color: 'gray'}} />
                <ResultRow label="Impôt commun individualisé" fieldName="total_tax" partnerIndex={partnerIndex} results={results} style={{}} />
                <ResultRow label="Déjà payé" fieldName="already_paid" partnerIndex={partnerIndex} results={results} style={{color: 'gray'}} />
                {(results.partners[partnerIndex].remains_to_pay && results.partners[1 - partnerIndex].remains_to_pay) &&
                    (<ResultRow label="Reste à payer" fieldName="remains_to_pay" partnerIndex={partnerIndex}
                    results={results} style={{fontSize: '1.5em'}} />)}
                {(results.partners[partnerIndex].remains_to_pay && results.partners[1 - partnerIndex].remains_to_get_back) &&
                    (<ResultRow label="Reste à payer aux impôts" fieldName="remains_to_pay" partnerIndex={partnerIndex}
                    results={results} style={{fontSize: '1.5em'}} />)}
                {(results.partners[partnerIndex].remains_to_get_back && results.partners[1 - partnerIndex].remains_to_pay) &&
                    (<ResultRow label="Reste à récupérer auprès de votre co-déclarant·e" fieldName="remains_to_get_back" partnerIndex={partnerIndex}
                    results={results} style={{fontSize: '1.5em'}} />)}
                 {(results.partners[partnerIndex].remains_to_get_back && results.partners[1 - partnerIndex].remains_to_get_back) &&
                    (<ResultRow label="Reste à récupérer" fieldName="remains_to_get_back" partnerIndex={partnerIndex} 
                    results={results} style={{fontSize: '1.5em'}} />)}
            </div>
        </div>
    )

export const ResultsPanel = ({ results }) => (
    <div>
        <div className="row">
            <div className="col-5">
                <Plot
                    data={[
                    {
                        x: [-1000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(140, 169, 255, 1.0)'},
                        hovertemplate: "[1] Reste à payer: 1 000 €"
                    },
                    {
                        x: [-4000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(138, 169, 237, .4)'},
                        hovertemplate: "[1] Déjà payé: 2 000 €"
                    },
                    {
                        x: [-2000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(0, 0, 0, .1)'},
                        hovertemplate: "[1] Gain par rapport à une déclaration séparée: 2 000 €"
                    },
                    
                    {
                        x: [1000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(140, 169, 255, 1.0)'},
                        hovertemplate: "[2] Reste à payer: 1 000 €"
                    },
                    {
                        x: [4000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(138, 169, 237, .4)'},
                        hovertemplate: "[2] Déjà payé: 2 000 €"
                    },
                    {
                        x: [2000],
                        y: ["montant"],
                        name: "",
                        type: 'bar',
                        orientation: 'h',
                        marker: {color: 'rgba(0, 0, 0, .1)'},
                        hovertemplate: "[2] Gain par rapport à une déclaration séparée: 2 000 €"
                    }
                    ]}
                    layout={{
                        width:'100%', height: 80, barmode: 'relative', showlegend: false,
                        margin: {l: 0, r: 0, b: 0, t: 0, pad: 0},
                        xaxis: {tickvals: []}, yaxis: {tickvals: []}
                    }}
                    config={{displayModeBar: false}}
                />
            </div>
        </div>
        <div className="row justify-content-center">
            <div className="p-3 col-md-6 col-xl-5">
                <ResultCard results={results} partnerIndex={0} />
            </div>
            <div className="p-3 col-md-6 col-xl-5">
                <ResultCard results={results} partnerIndex={1} />
            </div>
        </div>
    </div>
)
