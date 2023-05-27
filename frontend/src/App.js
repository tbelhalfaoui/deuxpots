import React, { createContext, useEffect, useRef, useState } from "react"
import { Accordion, AccordionStepItem } from './components/Accordion';
import './App.css';
import { Header } from './components/Header.js'
import { PdfSubmitForm } from './components/PdfSubmitForm.js'
import { TaxBoxesPanel } from "./components/TaxBoxesPanel.js";
import { ResultsPanel } from "./components/ResultsPanel.js";
import { Footer } from "./components/Footer.js";
import { SearchIndex } from "./components/searchIndex";

export const NavContext = createContext()

function App() {
  const [step, setStep] = useState({
    current: 1, // Index of the current pane displayed (between 1 and 3)
    max: 1      // Maximum pane index reached (enable going back to a previous step)
  })
  const [boxes, setBoxes] = useState([]);
  const [individualizedResults, setIndividualizedResults] = useState();
  const [isDemo, setIsDemo] = useState(false);
  const [warnings, setWarnings] = useState([]);
  const [errorMsgStep1, setErrorMsgStep1] = useState();
  const [errorMsgStep2, setErrorMsgStep2] = useState();
  const searchIndex = useRef();
  useEffect(
    () => {searchIndex.current = SearchIndex()},
  []);
  
  return (
      <div className="container py-4">
        <Header />
          <NavContext.Provider value={{ step, setStep }}>
            <Accordion>
              <AccordionStepItem title="1. Sélectionnez le fichier PDF de votre déclaration commune." itemStep={1}>
                <PdfSubmitForm setBoxes={setBoxes} setWarnings={setWarnings}
                errorMsg={errorMsgStep1} setErrorMsg={setErrorMsgStep1} resetErrorMsgs={() => setErrorMsgStep1(null) || setErrorMsgStep2(null)}
                setIsDemo={setIsDemo} searchIndex={searchIndex} />
              </AccordionStepItem>
              <AccordionStepItem title="2. Ajustez la répartition des montants déclarés." itemStep={2}>
                <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes}
                setIndividualizedResults={setIndividualizedResults} warnings={warnings}
                errorMsg={errorMsgStep2} setErrorMsg={setErrorMsgStep2} resetErrorMsgs={() => setErrorMsgStep2(null)}
                isDemo={isDemo} searchIndex={searchIndex} />
              </AccordionStepItem>
              <AccordionStepItem title="3. Résultats&nbsp;: vos impôts individualisés&nbsp;!" itemStep={3}>
                <ResultsPanel results={individualizedResults} />
              </AccordionStepItem>
            </Accordion>
          </NavContext.Provider>
        <Footer />
      </div>
  );
}

export default App;
