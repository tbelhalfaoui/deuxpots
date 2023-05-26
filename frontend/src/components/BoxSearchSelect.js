import { React, useState } from 'react';
import MiniSearch from 'minisearch'
import cerfaVariables from "../resources/cerfa_variables.json"

let miniSearch = new MiniSearch({
    fields: ['code', 'description', 'relatedCodes'],
    storeFields: ['code', 'description'],
    searchOptions: {
        boost: {
            code: 6,
            // description: 2,
            // relatedCodes: 1
        },
        fuzzy: 0.2,
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


export const BoxSearchSelect = ({ boxIndex, box, reassignBox }) => {
    const [ isBeingEdited, setIsBeingEdited ] = useState(false);
    const [ searchResults, setSearchResults ] = useState([]);
        
    const onSearchBoxChange = async (evt) => {
        const query = evt.target.value;
        const results = miniSearch.search(query);
        setSearchResults(results.slice(0, 20));
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
                                <button type="button" className="btn dropdown-item py-1 text-wrap"
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
