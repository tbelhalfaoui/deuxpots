import { FaGithub } from "react-icons/fa";
import { LegalNotice } from "./LegalNotice";

export const Footer = () => {
    return <div className="container text-center pt-4">
        <div className="row footerLink">
                Je développe ce site bénévolement et prends en compte vos retours avec plaisir,
                pour le faire fonctionner dans toutes les situations (et elles sont nombreuses !...).<br/>
                Alors s'il vous a été utile et si vous pouvez me soutenir financièrement, je vous en serais très reconnaissant :)
        </div>
        <div className="row footerLink py-1">
                <stripe-buy-button
                buy-button-id="buy_btn_1UAGAdC8zu98Ytw3yHJBd39N"
                publishable-key="pk_live_51UAFbxC8zu98Ytw3REVyjtMn9v5xOGBj0GrxYbwngmgAH9yrkJZzvuDqtrvec7hA40tIWnTBMgVDvnWzWaT2XuNB00uk6NJ0VU"
                >
                </stripe-buy-button>
        </div>
        <div className="row py-3">
            <div className="col-xl-5 py-1 py-xl-0">
                <a href="https://github.com/tbelhalfaoui/deuxpots" className="footerLink" target="_blank" rel="noreferrer">
                    Le code source de ce site est ouvert <FaGithub style={{color: 'gray'}} />
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