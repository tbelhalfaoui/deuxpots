import { useForm } from "react-hook-form";


export const PdfSubmitForm = ({setBoxes}) => {
    const { register, handleSubmit } = useForm();

    const sendTaxSheet = async (data) => {
        const formData = new FormData();
        formData.append("tax_pdf", data.file[0]);
        formData.append("boxes", "{}");
        await fetch("http://localhost:8888/individualize", {
            method: "POST",
            body: formData,
            mode: 'cors',
        }).then(
          res => res.json()
        ).then(
          res => {console.log(res); return res;}
        ).then(
          data => Object.fromEntries(
              data.boxes.map(box => [box.code, box])
            )
        ).then(
          boxes => setBoxes(boxes)
        );
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