import { React, useEffect, useState } from 'react';
import Fuse from "fuse.js";
import cerfaVariables from "../resources/cerfa_variables.json"

const fuse = new Fuse(cerfaVariables.flatMap(
    v => v.boxes.map(code => ({
        code: code,
        description: v.description,
        relatedCodes: v.boxes
    }))
),
{
    includeScore: true,
    keys: [
        {name: 'code', weight: 5},
        {name: 'description', weight: 2},
        {name: 'relatedCodes', weight: 1}
    ]
});


export const BoxSearchSelect = ({ boxIndex, box, reassignBox }) => {
    const [ isBeingEdited, setIsBeingEdited ] = useState(false);
    const [ searchResults, setSearchResults ] = useState([]);
        
    const onSearchBoxChange = async (evt) => {
        const query = evt.target.value;
        const results = fuse.search(query).map(result => result.item).slice(0, 20);
        setSearchResults(results);
    };

    return (
        (isBeingEdited) ?
            <div className="dropdown">
                <textarea className="form-control" rows="2" placeholder="Saisissez le code ou le nom de la case à ajouter."
                 autoFocus onChange={onSearchBoxChange} onBlur={() => setIsBeingEdited(false)} />
                {!!searchResults.length && 
                    <ul className="dropdown-menu show" style={{width: '100%'}}>
                        {searchResults.map(result => 
                            <li key={result.code}>
                                <button type="button" className="btn dropdown-item py-1" style={{'white-space': 'normal'}}
                                onMouseDown={() => reassignBox(boxIndex, result.code, result.description) || setIsBeingEdited(false)}>
                                    <strong>{result.code}</strong> - {result.description}
                                </button>
                            </li>
                        )}
                    </ul>}
            </div>
        : <label htmlFor={`raw_value.${boxIndex}`} className="form-label" onClick={() => setIsBeingEdited(true)}>
            {box.code} - {box.description}
          </label>
    );
};
