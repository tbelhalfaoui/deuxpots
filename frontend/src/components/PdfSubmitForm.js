import { useForm } from "react-hook-form";


export const PdfSubmitForm = ({setBoxes, setStep}) => {
    const { register, handleSubmit } = useForm();

    const sendTaxSheet = async (data) => {
        const formData = new FormData();
        formData.append("tax_pdf", data.file[0]);
        await fetch("http://localhost:8888/parse", {
            method: "POST",
            body: formData,
            mode: 'cors',
        }).then(
          res => res.json()
        ).then(
          data => Object.fromEntries(
            data.boxes.sort(
              (box1, box2) => box1.code.localeCompare(box2.code)
            ).map(box => [box.code, {
              ...box,
              description: box.description,
              original_raw_value: box.raw_value,
              original_attribution: box.attribution,
              partner_0_value: box.raw_value * (1 - box.attribution),
              partner_1_value: box.raw_value * box.attribution,
            }])
          )
        ).then(
          setBoxes
        ).then(
          setStep(2)
        )
    }

    return (
        <form onSubmit={handleSubmit(sendTaxSheet)}>
        <div class="container py-4 text-center" id="containerStep1">
           <div class="row gx-10 justify-content-center">
             <div class="col-4">
               <input type="file" class="form-control" {...register("file")} />
             </div>
             <div class="col-1">
               <input type="submit" class="btn btn-primary" />
             </div>
           </div>
          </div>
        </form>
    )
}