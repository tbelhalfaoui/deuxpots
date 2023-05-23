import { FaGithub } from "react-icons/fa";
import { LegalNotice } from "./LegalNotice";

export const Footer = () => {
    return <div className="container text-center pt-4">
        <div className="row">
            <div className="col-xl-5 py-1 py-xl-0">
                <a className="footerLink" href="https://github.com/tbelhalfaoui/deuxpots">
                    Le code source de ce site est ouvert <a href="https://github.com/tbelhalfaoui/deuxpots" target="_blank" rel="noreferrer">
                        <FaGithub style={{color: 'gray'}} />
                    </a>
                </a>
            </div>
            <div className="col-xl-2 py-1 py-xl-0">
                <button type="button" className="btn footerLink py-0" data-bs-toggle="modal" data-bs-target="#legalNoticeModal">
                    Mention légales
                </button>
                <LegalNotice />
            </div>
            <div className="footerLink col-xl-5 py-1 py-xl-0">
                Toute remarque est la bienvenue&nbsp;: contact@deuxpots.fr
            </div>
        </div>
    </div>
}