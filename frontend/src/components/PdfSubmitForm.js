import React, { useState } from "react"


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
          e => setErrorMsg(e.message)
        ).finally(
          () => setIsLoading(false)
        );
    }

    return (
        <form onSubmit={sendTaxSheet}>
          {errorMsg && 
          (<div class="alert alert-danger" role="alert">
            {errorMsg}
          </div>)}
          <div class="container py-4 text-center" id="containerStep1">
           <div class="row justify-content-center">
             <div class="col-md-5 col-xl-4">
               <input type="file" class="form-control" name="taxFile" onChange={sendTaxSheet} disabled={isLoading} />
             </div>
             <div class="py-2 col-1">
              ou
             </div>
             <div class="col-md-5 col-xl-3">
               <button type="submit" class="btn btn-primary" name="tryOnExample">
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