import React, { useEffect, useState } from "react"
import { useForm } from "react-hook-form";
import { Header } from './components/Header.js'
import { PdfSubmitForm } from './components/PdfSubmitForm.js'
import './App.css';
import { TaxBoxesPanel } from "./components/TaxBoxesPanel.js";



function App() {
  const [boxes, setBoxes] = useState([]);
  const [step, setStep] = useState(0);

  return (
      <div class="container">
        <Header />
        <PdfSubmitForm setBoxes={setBoxes} step={step} setStep={setStep} />
        <TaxBoxesPanel boxes={boxes} setBoxes={setBoxes} step={step} setStep={setStep} />
      </div>
  );
}

export default App;
