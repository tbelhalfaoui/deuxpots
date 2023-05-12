export const Accordion = ({ children }) => (
    <div class="accordion" id="accordionStepsNav">
        {children}
    </div>
)

export const AccordionItem = ({ title, name, isExpanded, onExpand, enabled, children }) => (
    <div class="accordion-item">
        <h2 class="accordion-header" id={`heading-${name}`}>
            <button class={`accordion-button ${(!isExpanded) && "collapsed"}`} type="button" data-bs-toggle="collapse"
            aria-expanded={isExpanded} aria-controls={`collapse-${name}`} onClick={onExpand} disabled={!enabled}
            style={(!enabled) ? {color: 'gray'} : {'font-weight': 'bold'}}>
                {title}
            </button>
        </h2>
        <div id={`collapse-${name}`} class={`accordion-collapse collapse ${(isExpanded) && "show"}`}
            aria-labelledby={`heading-${name}`}data-bs-parent="#accordionStepsNav">
            <div class="accordion-body">
                {children}
            </div>
        </div>
    </div>
) 


export const AccordionStepItem = ({ title, itemStep, currentStep, maxCurrentStep, setStep, children }) => (
    <AccordionItem title={title} name={`step${itemStep}`}
    isExpanded={currentStep === itemStep}
    onExpand={() => setStep(itemStep)}
    enabled={itemStep <= maxCurrentStep}>
        {children}
    </AccordionItem>
)