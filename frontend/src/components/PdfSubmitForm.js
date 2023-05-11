import { useForm } from "react-hook-form";
import React, { useState } from "react"
import { SubmitButton } from "./SubmitButton";


export const PdfSubmitForm = ({setBoxes, setStep, isError}) => {
    const { register, handleSubmit } = useForm();
    const [errorMsg, setErrorMsg] = useState();
    const [isLoading, setIsLoading] = useState(false);


    const sendTaxSheet = async (data) => {
        setIsLoading(true);

        const formData = new FormData();
        formData.append("tax_pdf", data.file[0]);
        await fetch("http://localhost:8888/parse", {
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
              partner_0_value: box.attribution && (box.raw_value * (1 - box.attribution)),
              partner_1_value: box.attribution && (box.raw_value * box.attribution),
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
    }

    return (
        <form onSubmit={handleSubmit(sendTaxSheet)}>
          {errorMsg && 
          (<div class="alert alert-danger" role="alert">
            {errorMsg.message}
          </div>)}
          <div class="container py-4 text-center" id="containerStep1">
           <div class="row gx-10 justify-content-center">
             <div class="col-4">
               <input type="file" class="form-control" {...register("file")} />
             </div>
             <div class="col-2">
              <SubmitButton isLoading={isLoading} />
             </div>
           </div>
          </div>
        </form>
    )
}