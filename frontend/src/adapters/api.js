const API_ROOT_URL = `${process.env.REACT_APP_API_URL || window.location.origin}`

export const callPaseRoute = async (fileContent, isDemo) => {
    console.log(fileContent, isDemo)
    const formData = new FormData();
    const queryParams = new URLSearchParams();

    if (isDemo) {
      queryParams.append("demo", "true");
    }
    else {
      formData.append("tax_pdf", fileContent);
    }

    return await fetch(`${API_ROOT_URL}/parse?${queryParams}`, {
        method: "POST",
        body: formData,
    }).then(
      res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
    ).then(
      res => res.json()
    );
}

export const callIndividualizeRoute = async (boxes, isDemo) => {
    const queryParams = new URLSearchParams()
    if (isDemo) {
        queryParams.append("demo", "true")
    }
    
    return await fetch(`${API_ROOT_URL}/individualize?${queryParams}`, {
        method: "POST",
        body: JSON.stringify({'boxes': boxes}),
        mode: 'cors',
        headers: {
            'Content-type':'application/json', 
            'Accept':'application/json'
        }
    }).then(
        res => (!res.ok) ? res.text().then(text => {throw new Error(text)}) : res
    ).then(
      res => res.json()
    )
}