import { FaInfoCircle, FaExclamationTriangle, FaTimesCircle } from "react-icons/fa";


export const ErrorMessage = ({ error }) =>
    error &&
    (<div className="alert alert-danger" role="alert">
        <FaTimesCircle /> {
            (error instanceof TypeError) ?
                `Impossible de se connecter au serveur.
                 Il s'agit d'un problème temporaire, soit avec le serveur ou avec votre connexion Internet.`
            : (error instanceof Error) ? error.message
            : error  // string error from frontend
        }
    </div>)

export const HelpMessageForParser = ({ error }) =>
    error &&
    (<div className="alert alert-primary" role="alert">
        <FaInfoCircle /> Vous pouvez trouver votre déclaration sur le <a href="https://cfspart.impots.gouv.fr/"><strong>site des impôts</strong></a>,
        dans la rubrique <strong>Documents</strong>, en cliquant sur <strong>PDF</strong> à côté de <strong>Déclaration en ligne des revenus 20xx</strong>.<br/>
        Si le problème persiste, n'hésitez pas à écrire à <strong>contact@deuxpots.fr</strong>
    </div>)

export const WarningMessage = ({ warning }) => 
    warning && 
    (<div className="alert alert-warning" role="alert">
        <FaExclamationTriangle /> {warning}
    </div>)
