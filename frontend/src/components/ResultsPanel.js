import { useState } from "react";
import { FaInfoCircle } from "react-icons/fa";

const ResultRow = ({ label, value, style }) =>
    <div className="py-1 row" style={style}>
        <div className="col-lg-8">
            {label}&nbsp;:
        </div>
        <div className="col-lg-4 text-end">
            <strong>{ Math.round(value).toLocaleString('fr-FR') }&nbsp;€</strong>
        </div>
    </div>

const FinalResult = ({ partners, partnerIndex }) =>
    <div>
        {(partners[partnerIndex].remains_to_pay_to_tax_office > 0) &&
            <ResultRow label="Reste à payer aux impôts" style={{fontSize: '1.5em'}}
                value={partners[partnerIndex].remains_to_pay_to_tax_office} />}
        {(partners[partnerIndex].remains_to_pay_to_tax_office < 0) &&
            <ResultRow label="Reste à récupérer des impôts" style={{fontSize: '1.5em'}}
            value={-partners[partnerIndex].remains_to_pay_to_tax_office} />}
        {(partners[partnerIndex].remains_to_pay_to_partner > 0) &&
            <ResultRow label="Reste à payer à votre co-déclarant·e" style={{fontSize: '1.5em'}}
            value={partners[partnerIndex].remains_to_pay_to_partner} />}
        {(partners[partnerIndex].remains_to_pay_to_partner < 0) &&
            <ResultRow label="Reste à récupérer auprès de votre co-déclarant·e" style={{fontSize: '1.5em'}}
            value={-partners[partnerIndex].remains_to_pay_to_partner} />}
        {(partners[partnerIndex].remains_to_pay_to_tax_office === 0) && (partners[partnerIndex].remains_to_pay_to_partner === 0) &&
            <ResultRow label="Reste à payer" fieldName="remains_to_pay_to_tax_office" style={{fontSize: '1.5em'}}
            value={0} />}
    </div>

const ResultCard = ({ partners, partnerIndex }) =>
    partners && (
        <div className="card">
            <div className="card-header">
                Déclarant·e {partnerIndex + 1}
            </div>
            <div className="card-body">
                <ResultRow label="Impôt si déclaration séparée" style={{color: 'gray'}}
                    value={partners[partnerIndex].tax_if_single} />
                <ResultRow label="Impôt commun individualisé" style={{}}
                    value={partners[partnerIndex].total_tax} />
                <ResultRow label="Déjà payé" style={{color: 'gray'}}
                    value={partners[partnerIndex].already_paid} />
                <FinalResult partners={partners} partnerIndex={partnerIndex} />
            </div>
        </div>
    )

export const ResultsPanel = ({ results }) => {
    const [gainSplitMethod, setGainSplitMethod] = useState("equal");
    const handleSplitMethodChange = (evt) => setGainSplitMethod(evt.target.value)
    if (!results) {
        return
    }

    const partners = (gainSplitMethod === "equal") ? results.partners_equal_split : results.partners_proportional_split
    return <div>
        {(results.total_tax_gain > 10) &&
        <div className="row">
            <div className="col-12">
                <div className="alert alert-primary" role="alert">
                    <FaInfoCircle /> <strong>La déclaration commune induit une baisse de l'impôt total de {results.total_tax_gain.toLocaleString('fr-FR')} €.
                    Comment souhaitez-vous répartir cette somme&nbsp;?</strong>
                    <form>
                        <div className="row">
                            <div className="col-lg-6">
                                <div className="form-check">
                                    <input className="form-check-input" type="radio" name="flexRadioDefault" id="radioSplitEqual"
                                    value="equal" onChange={handleSplitMethodChange} checked={gainSplitMethod === "equal"} />
                                    <label className="form-check-label" for="radioSplitEqual">
                                        À parts égales ({Math.round(results.partners_equal_split[0].tax_gain).toLocaleString('fr-FR')}&nbsp;€ chacun·e),
                                    </label>
                                </div>
                            </div>
                                <div className="col-lg-6">
                                    <div className="form-check">
                                    <input className="form-check-input" type="radio" id="radioSplitProportional" name="flexRadioDefault"
                                    value="proportional" onChange={handleSplitMethodChange} checked={gainSplitMethod === "proportional"} />
                                    <label className="form-check-label" for="radioSplitProportional">
                                        En proportion de l'impôt dû
                                        ({Math.round(results.partners_proportional_split[0].tax_gain).toLocaleString('fr-FR')}&nbsp;€
                                        et {Math.round(results.partners_proportional_split[1].tax_gain).toLocaleString('fr-FR')}&nbsp;€).
                                    </label>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>}
        <div className="row justify-content-center">
            <div className="p-3 col-md-6 col-xl-5">
                <ResultCard partners={partners} partnerIndex={0} />
            </div>
            <div className="p-3 col-md-6 col-xl-5">
                <ResultCard partners={partners} partnerIndex={1} />
            </div>
        </div>
    </div>
}
