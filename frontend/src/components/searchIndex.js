import MiniSearch from 'minisearch'
import cerfaVariables from "../resources/cerfa_variables.json"

const HOUSEHOLD_STATUS_BOXES = ['0AM', '0AO', '0AD', '0AC', '0AV']


export const SearchIndex = () => {
    const miniSearch = new MiniSearch({
        fields: ['code', 'description', 'relatedCodes'],
        storeFields: ['code', 'description', 'type'],
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
            type: v.type,
            relatedCodes: v.boxes,
        }))
    ))
    var blackList = HOUSEHOLD_STATUS_BOXES

    const search = (query, limit) =>
        miniSearch.search(query, { 
            filter: result => !blackList.includes(result.code)
        }).slice(0, limit)
    
    const disable = (codeToDisable) => 
        blackList.push(codeToDisable)
    
    const reEnable = (codeToEnable) =>
        blackList = blackList.filter(code => code !== codeToEnable)
    
    return { search, disable, reEnable }
};

// export const createSearchIndex = () => {
//     const miniSearch = new MiniSearch({
//         fields: ['code', 'description', 'relatedCodes'],
//         storeFields: ['code', 'description'],
//         searchOptions: {
//             boost: {
//                 code: 6,
//                 description: 2,
//                 relatedCodes: 1
//             },
//             fuzzy: 0.25,
//             prefix: true,
//         }
//     })
//     miniSearch.addAll(cerfaVariables.flatMap(
//         v => v.boxes.map(code => ({
//             id: code,
//             code: code,
//             description: v.description,
//             relatedCodes: v.boxes
//         }))
//     ).filter(
//         box => !HOUSEHOLD_STATUS_BOXES.includes(box.code)
//     ));
//     return miniSearch
// }