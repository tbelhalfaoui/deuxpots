import React, { useEffect, useState } from "react"
import { useForm } from "react-hook-form";
import { Header } from './components/Header.js'
import { PdfSubmitForm } from './components/PdfSubmitForm.js'
import { Accordion, AccordionStepItem } from './components/Accordion';
import './App.css';
import { TaxBoxesPanel } from "./components/TaxBoxesPanel.js";


function App() {
  const [boxes, setBoxes] = useState([]);
  const [step, setStep_] = useState(1);
  const [maxStep, setMaxStep_] = useState(1);
  
  const setStep = (s) => {
    console.log({"setStep": s});
    setStep_(s);
  };

  const setMaxStep = (s) => {
    console.log({"setMaxStep": s});
    setMaxStep_(s);
  };

  return (
      <div class="container">
        <Header />
        {/* <Accordion activeKey={step.toString()}>
            <Accordion.Item eventKey="1" disabled>
            <Accordion.Header>1. Sélectionnez le fichier PDF de votre déclaration commune.</Accordion.Header>
            <Accordion.Body>
              <PdfSubmitForm setBoxes={setBoxes} setStep={setStep} />
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="2">
            <Accordion.Header>2. Vérifiez l'attribution des cases à chaque déclarant·e.</Accordion.Header>
            <Accordion.Body>
              <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes} setStep={setStep} />
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="3">
            <Accordion.Header>3. Résultats: l'impôt individualisé!</Accordion.Header>
            <Accordion.Body>
              TODO
            </Accordion.Body>
          </Accordion.Item>
        </Accordion> */}
        <Accordion>
          <AccordionStepItem title="1. Sélectionnez le fichier PDF de votre déclaration commune."
          itemStep="1" currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <PdfSubmitForm setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)} />
          </AccordionStepItem>
          <AccordionStepItem title="2. Vérifiez l'attribution des cases à chaque déclarant·e."
          itemStep="2" currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)} />
          </AccordionStepItem>
          <AccordionStepItem title="3. Résultats: l'impôt individualisé!"
          itemStep="3" currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            TODO
          </AccordionStepItem>
        </Accordion>
      </div>
  );
}

export default App;
