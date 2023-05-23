import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleInfo } from "@fortawesome/free-solid-svg-icons";
import React, { useState } from "react"
import { ErrorMessage, HelpMessageForParser } from "./Alert.js";


export const PdfSubmitForm = ({setBoxes, setStep, setWarnings, errorMsg, setErrorMsg, resetErrorMsgs}) => {
    const [isLoading, setIsLoading] = useState(false);

    const sendTaxSheet = async (evt) => {
        evt.preventDefault();
        setIsLoading(true);

        const formData = new FormData();
        const queryParams = new URLSearchParams();
        if (evt.target.tryOnExample) {
          queryParams.append("demo", "true");
        }
        else {
          formData.append("tax_pdf", evt.target.files[0]);
        }
        
        await fetch(`${process.env.REACT_APP_API_URL}/parse?${queryParams}`, {
            method: "POST",
            body: formData,
        }).then(
          res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
        ).then(
          res => res.json(),
        ).then(
          data => 
            setBoxes(
              data.boxes.sort(
                (box1, box2) => box1.code.localeCompare(box2.code)
              ).map(box => ({
                ...box,
                description: box.description,
                partner_0_value: ((box.attribution || (box.attribution === 0)) && box.raw_value) ? box.raw_value * (1 - box.attribution) : "",
                partner_1_value: ((box.attribution || (box.attribution === 0)) && box.raw_value) ? box.raw_value * box.attribution : "",
                totalIsLocked: !!box.raw_value
              }))
            ) || setWarnings(data.warnings)
        ).then(
          () => setStep(2) || resetErrorMsgs()
        ).catch(
          e => setErrorMsg(e)
        ).finally(
          () => setIsLoading(false)
        );

        evt.target.value = '';  // makes onChange to be triggered again, even if re-uploading the same file
    }

    return (
        <form onSubmit={sendTaxSheet}>
          <ErrorMessage error={errorMsg} />
          <HelpMessageForParser error={errorMsg} />
          {!errorMsg && 
            (<div className="alert alert-primary" role="alert">
                <FontAwesomeIcon icon={faCircleInfo} /> Aucune donnée issue de votre déclaration d'impôt ne sera collectée.<br/>
                Seuls les montants, anonymes, seront utilisés temporairement pour faire le calcul de votre impôt.
            </div>)
          }
          <div className="container py-4 text-center" id="containerStep1">
            <div className="row justify-content-center">
              <div className="col-md-5 col-xl-4">
                <input type="file" className="form-control" name="taxFile" onChange={sendTaxSheet} disabled={isLoading} />
              </div>
              <div className="py-2 col-1">
                ou
              </div>
              <div className="col-md-5 col-xl-3">
                <button type="submit" className="btn btn-primary" name="tryOnExample" disabled={isLoading}>
                  Essayer sur un exemple
                </button>
              </div>
              {isLoading && (
                <div className="spinner-border" role="status">
                  <span className="sr-only"></span>
                </div>
                )}
             </div>
            </div>
        </form>
    )
}