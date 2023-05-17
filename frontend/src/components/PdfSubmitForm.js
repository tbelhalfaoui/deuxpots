import React, { useState } from "react"
import { ErrorMessage } from "./ErrorMessage.js";


export const PdfSubmitForm = ({setBoxes, setStep, isError}) => {
    const [errorMsg, setErrorMsg] = useState();
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
            mode: 'cors',
        }).then(
          res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
        ).then(
          res => res.json(),
        ).then(
          data => Object.fromEntries(
            data.boxes.sort(
              (box1, box2) => box1.code.localeCompare(box2.code)
            ).map(box => [box.code, {
              ...box,
              description: box.description,
              original_raw_value: box.raw_value,
              original_attribution: box.attribution,
              partner_0_value: (box.attribution || (box.attribution === 0)) ? box.raw_value * (1 - box.attribution) : "",
              partner_1_value: (box.attribution || (box.attribution === 0)) ? box.raw_value * box.attribution : "",
            }])
          )
        ).then(
          setBoxes
        ).then(
          () => setErrorMsg(null) || setStep(2)
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
          <div class="alert alert-primary" role="alert">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
              </svg> Aucune donnée issue de votre déclaration d'impôt ne sera collectée.<br/>
              Seuls les montants, anonymes, seront utilisés temporairement pour faire la simulation.
          </div>
          <div class="container py-4 text-center" id="containerStep1">
            <div class="row justify-content-center">
              <div class="col-md-5 col-xl-4">
                <input type="file" class="form-control" name="taxFile" onChange={sendTaxSheet} disabled={isLoading} />
              </div>
              <div class="py-2 col-1">
                ou
              </div>
              <div class="col-md-5 col-xl-3">
                <button type="submit" class="btn btn-primary" name="tryOnExample" disabled={isLoading}>
                  Essayer sur un exemple
                </button>
              </div>
              {isLoading && (
                <div class="spinner-border" role="status">
                  <span class="sr-only"></span>
                </div>
                )}
             </div>
            </div>
        </form>
    )
}