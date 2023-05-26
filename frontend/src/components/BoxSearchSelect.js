import { React, useState } from 'react';
import { Modal, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import MiniSearch from 'minisearch'
import cerfaVariables from "../resources/cerfa_variables.json"

let miniSearch = new MiniSearch({
    fields: ['code', 'description', 'relatedCodes'],
    storeFields: ['code', 'description'],
    searchOptions: {
        boost: {
            code: 6,
            description: 2,
            relatedCodes: 1
        },
        fuzzy: 0.25,
        prefix: true,
    }
  })
miniSearch.addAll(cerfaVariables.flatMap(
    v => v.boxes.map(code => ({
        id: code,
        code: code,
        description: v.description,
        relatedCodes: v.boxes
    }))
).filter(
    box => !['0AM', '0AO', '0AD', '0AC', '0AV'].includes(box.code)
));

export const ReassignBoxModal = ({ box, chosenResult, show, closeModal, onConfirm }) =>
    (chosenResult &&
    <Modal show={chosenResult} onHide={closeModal} size="lg" centered>
        <Modal.Header closeButton>
            <Modal.Title>Voulez-vous modifier l'intitulé de cette case ?</Modal.Title>
        </Modal.Header>
            <Modal.Body>
                <p>
                    L'ancien intitulé: <mark>{box.code} - {box.description}</mark>
                </p>
                <p>
                    Nouvel intitulé: <mark>{chosenResult.code} - {chosenResult.description}</mark>
                </p>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={closeModal}>
                    Conserver l'ancien
                </Button>
                <Button variant="primary" onClick={onConfirm}>
                    Confirmer
                </Button>
        </Modal.Footer>
    </Modal>);


export const BoxSearchSelect = ({ boxIndex, box, reassignBox }) => {
    const [ isBeingEdited, setIsBeingEdited ] = useState(false);
    const [ searchResults, setSearchResults ] = useState([]);
    const [ chosenResult, setChosenResult ] = useState();

    const onSearchBoxChange = async (evt) => {
        const query = evt.target.value;
        const results = miniSearch.search(query);
        setSearchResults(results.slice(0, 20));
    };

    const onChooseResult = (result) => {
        if (!box.code) {
            // Assigning empty box
            reassignBox(boxIndex, result.code, result.description);
        }
        else if (box.code !== result.code) {
            // Reassigning an existing box: open modal for confirmation
            setChosenResult({...result})
        }
        setIsBeingEdited(false);
        setSearchResults([]);
    }

    return (
        <div>
            {(isBeingEdited || !box.code) ?
                <div>
                    <div className="dropdown">
                        <textarea className="form-control" rows="2" placeholder="Saisissez le code ou le nom de la case à ajouter."
                        autoFocus={box.code} onChange={onSearchBoxChange} onBlur={() => setIsBeingEdited(false)} />
                        {!!searchResults.length && 
                            <ul className="dropdown-menu show" style={{width: '100%'}}>
                                {searchResults.map(result => 
                                    <li key={result.code}>
                                        <button type="button" className="btn dropdown-item py-1 text-wrap"
                                        onMouseDown={() => onChooseResult(result)}>
                                            <strong>{result.code}</strong> - {result.description}
                                        </button>
                                    </li>
                                )}
                            </ul>}
                    </div>
                </div>
            : <OverlayTrigger placement="top" overlay={
                    <Tooltip id="tooltipEdit">
                        Cliquez ici pour modifier l'intitulé de cette ligne.
                    </Tooltip>
                }><label htmlFor={`raw_value.${boxIndex}`} className="form-label" onClick={() => setIsBeingEdited(true)}>
                    {box.code} - {box.description}
                </label>
              </OverlayTrigger>
            }
            <ReassignBoxModal boxIndex={boxIndex} box={box} chosenResult={chosenResult} closeModal={() => setChosenResult(undefined)}
            onConfirm={() => reassignBox(boxIndex, chosenResult.code, chosenResult.description) || setChosenResult(undefined)} />
        </div>
    );
};
