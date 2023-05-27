import { useContext } from "react"
import { NavContext } from "../App.js"

export const Accordion = ({ children }) => (
    <div className="accordion" id="accordionStepsNav">
        {children}
    </div>
)

export const AccordionItem = ({ title, name, isExpanded, onExpand, enabled, children }) => (
    <div className="accordion-item">
        <h2 className="accordion-header" id={`heading-${name}`}>
            <button className={`accordion-button ${(!isExpanded) && "collapsed"}`} type="button" data-bs-toggle="collapse"
            aria-expanded={isExpanded} aria-controls={`collapse-${name}`} onClick={onExpand} disabled={!enabled}
            style={(!enabled) ? {color: 'gray'} : {fontWeight: 'bold'}}>
                {title}
            </button>
        </h2>
        <div id={`collapse-${name}`} className={`accordion-collapse collapse ${(isExpanded) && "show"}`}
            aria-labelledby={`heading-${name}`}data-bs-parent="#accordionStepsNav">
            <div className="accordion-body">
                {children}
            </div>
        </div>
    </div>
) 


export const AccordionStepItem = ({ title, itemStep, children }) => {
    const { step, setStep } = useContext(NavContext)

    return (
        <AccordionItem title={title} name={`step${itemStep}`}
        isExpanded={step.current === itemStep}
        onExpand={() => setStep({...step, current: itemStep})}
        enabled={itemStep <= step.max}>
            {children}
        </AccordionItem>
    )
}