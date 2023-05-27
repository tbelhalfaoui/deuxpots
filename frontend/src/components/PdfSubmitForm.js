import { FaInfoCircle } from "react-icons/fa";
import React, { useState } from "react"
import { ErrorMessage, HelpMessageForParser } from "./Alert.js";


export const PdfSubmitForm = ({setBoxes, setStep, setWarnings, errorMsg, setErrorMsg, resetErrorMsgs, setIsDemo, searchIndex}) => {
    const [isLoading, setIsLoading] = useState(false);

    const sendTaxSheet = async (evt) => {
        setIsLoading(true);

        const formData = new FormData();
        const queryParams = new URLSearchParams();
        const isDemo = evt.target.name === "tryOnExample";
        setIsDemo(isDemo);

        if (isDemo) {
          queryParams.append("demo", "true");
        }
        else {
          formData.append("tax_pdf", evt.target.files[0]);
        }
        
        await fetch(`${process.env.REACT_APP_API_URL || window.location.origin}/parse?${queryParams}`, {
            method: "POST",
            body: formData,
        }).then(
          res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
        ).then(
          res => res.json(),
        ).then(
          data => {
            setWarnings(data.warnings);
            return data.boxes.sort(
              (box1, box2) => box1.code.localeCompare(box2.code)
            ).map(box => ({
              ...box,
              description: box.description,
              partner_0_value: ((box.attribution || (box.attribution === 0)) && box.raw_value) ? box.raw_value * (1 - box.attribution) : "",
              partner_1_value: ((box.attribution || (box.attribution === 0)) && box.raw_value) ? box.raw_value * box.attribution : "",
              totalIsLocked: !isDemo && !!box.raw_value
            })).concat([{
                code: "",
                raw_value: "",
                description: "",
                partner_0_value: "",
                partner_1_value: "",
                attribution: null,
                totalIsLocked: false
            }])
          }
        ).then(
          boxes => boxes.forEach(box => searchIndex.current.disable(box.code)) || boxes
        ).then(
          setBoxes
        ).then(
          () => setStep(2) || resetErrorMsgs()
        ).finally(
          () => setIsLoading(false)
        );

        evt.target.value = '';  // makes onChange to be triggered again, even if re-uploading the same file
    }

    return (
        <form>
          <ErrorMessage error={errorMsg} />
          <HelpMessageForParser error={errorMsg} />
          {!errorMsg && 
            (<div className="alert alert-primary" role="alert">
                <FaInfoCircle /> Aucune donnée issue de votre déclaration d'impôt ne sera collectée.<br/>
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
                <button type="button" className="btn btn-primary" name="tryOnExample" onClick={sendTaxSheet} disabled={isLoading}>
                  Remplir à partir d'un exemple
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