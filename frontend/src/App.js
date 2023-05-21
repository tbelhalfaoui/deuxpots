import React, { useState } from "react"
import { Accordion, AccordionStepItem } from './components/Accordion';
import './App.css';
import { Header } from './components/Header.js'
import { PdfSubmitForm } from './components/PdfSubmitForm.js'
import { TaxBoxesPanel } from "./components/TaxBoxesPanel.js";
import { ResultsPanel } from "./components/ResultsPanel.js";


function App() {
  const [boxes, setBoxes] = useState([]);
  const [individualizedResults, setIndividualizedResults] = useState();
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);
  const [warnings, setWarnings] = useState([]);
  
  return (
      <div className="container py-4">
        <Header />
        <Accordion>
          <AccordionStepItem title="1. Sélectionnez le fichier PDF de votre déclaration commune."
          itemStep={1} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <PdfSubmitForm setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)} setWarnings={setWarnings} />
          </AccordionStepItem>
          <AccordionStepItem title="2. Ajustez la répartition des montants déclarés."
          itemStep={2} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)}
            setIndividualizedResults={setIndividualizedResults} warnings={warnings} />
          </AccordionStepItem>
          <AccordionStepItem title="3. Résultats&nbsp;: vos impôts individualisés&nbsp;!"
          itemStep={3} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <ResultsPanel results={individualizedResults} />
          </AccordionStepItem>
        </Accordion>
        <div className="text-center pt-4">
          <a className="footerLink" href="https://github.com/tbelhalfaoui/deuxpots">Le code source de ce site est ouvert : https://github.com/tbelhalfaoui/deuxpots</a>
        </div>
      </div>
  );
}

export default App;
