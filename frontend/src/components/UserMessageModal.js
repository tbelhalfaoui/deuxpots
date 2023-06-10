import React, { useContext } from "react"
import { Modal } from 'react-bootstrap';
import { FaInfoCircle, FaExclamationTriangle, FaTimesCircle } from "react-icons/fa";
import { UserMessagesContext } from "../App.js";


export const UserMessage = ({ msg }) => {
    switch (msg.level)  {
        case "error":
            return <div className="alert alert-danger" role="alert">
                <FaTimesCircle /> {
                    (msg.message instanceof TypeError) ?
                        `Impossible de se connecter au serveur.
                        Il s'agit d'un problème temporaire, soit avec le serveur ou avec votre connexion Internet.`
                    : (msg.message instanceof Error) ? msg.message.message
                    : msg.message  // string error from frontend
                }
            </div>
        case "warning":
            return <div className="alert alert-warning" role="alert">
                <FaExclamationTriangle /> {msg.message}
            </div>
        case "info":
            return <div className="alert alert-primary" role="alert">
                <FaInfoCircle /> {msg.message}
            </div>
        default:
            throw new Error(`Unknown message level ${msg.level}`);
    }
}

export const UserMessageModal = () => {
    const { userMessages, setUserMessages } = useContext(UserMessagesContext);

    return ((userMessages.length > 0) &&
        <Modal show={true} size="lg" centered
         onHide={() => setUserMessages([])}>
            <Modal.Header closeButton>
                <Modal.Title>Attention</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {userMessages.map((msg, idx) => 
                    <UserMessage key={idx} msg={msg} />
                )}
            </Modal.Body>
        </Modal>)
}