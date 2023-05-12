import React, { useState } from "react"
import { Header } from './components/Header.js'
import { PdfSubmitForm } from './components/PdfSubmitForm.js'
import { Accordion, AccordionStepItem } from './components/Accordion';
import './App.css';
import { TaxBoxesPanel } from "./components/TaxBoxesPanel.js";
import { ResultsPanel } from "./components/ResultsPanel.js";


function App() {
  const [boxes, setBoxes] = useState([]);
  const [individualizedResults, setIndividualizedResults] = useState();
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);
  
  return (
      <div class="container py-4">
        <Header />
        <Accordion>
          <AccordionStepItem title="1. Sélectionnez le fichier PDF de votre déclaration commune."
          itemStep={1} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <PdfSubmitForm setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)} />
          </AccordionStepItem>
          <AccordionStepItem title="2. Vérifiez l'attribution des cases à chaque déclarant·e."
          itemStep={2} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes} setStep={(s) => setStep(s) || setMaxStep(s)}
            setIndividualizedResults={setIndividualizedResults} />
          </AccordionStepItem>
          <AccordionStepItem title="3. Résultats: l'impôt individualisé!"
          itemStep={3} currentStep={step} maxCurrentStep={maxStep} setStep={setStep}>
            <ResultsPanel results={individualizedResults} />
          </AccordionStepItem>
        </Accordion>
      </div>
  );
}

export default App;
