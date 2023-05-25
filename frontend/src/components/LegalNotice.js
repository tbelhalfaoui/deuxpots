export const LegalNotice = () => 
    <div className="modal modal-lg fade" id="legalNoticeModal" tabIndex="-1" aria-labelledby="legalNoticeModalLabel" aria-hidden="true">
        <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
            <div className="modal-content">
            <div className="modal-header">
                <h1 className="modal-title display-6" id="legalNoticeModalLabel">Mentions légales</h1>
                <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div className="modal-body text-start">
                <div className="py-2">
                    <h4>Responsable</h4>
                    <p>
                        <em>Deux pots</em> est développé et édité à titre personnel par <mark>Thomas&nbsp;Belhalfaoui</mark>.
                    </p>
                    <p>
                        Pour toute demande ou question, merci d'écrire à <mark>contact@deuxpots.fr</mark>.
                    </p>
                </div>
                <div className="py-2">
                    <h4>Hébergement</h4>
                    <p>
                        Ce site est hébergé par la société <mark>Fly.io, Inc.</mark>, domiciliée 2045 West Grand Avenue Ste B, Chicago, IL 60612,
                        et joignable à ces coordonnées : +13126264490 / ops@fly.io.
                    </p>
                </div>
                <div className="py-2">
                    <h4>Transparence</h4>
                    <p>
                        Le <mark>code source de ce site est public</mark>. Il est accessible à cette 
                        adresse : <a href="https://github.com/tbelhalfaoui/deuxpots" target="_blank" rel="noreferrer">
                        https://github.com/tbelhalfaoui/deuxpots</a>.
                        Celles et ceux qui le souhaitent peuvent en prendre connaissance et réaliser un audit. Les conseils sont les bienvenus.
                    </p>
                </div>
                <div className="py-2">
                    <h4>Données personnelles</h4>
                    <p>
                        <mark>Aucune donnée à caractère personnel</mark> n'est collectée.
                    </p>
                    <p>
                        Ce site n'utilise <mark>pas de cookies</mark>.
                    </p>
                    <p>
                        Les fichiers PDF de déclaration d'impôt envoyés sur le site sont utilisés uniquement pour en extraire
                        les nombres nécessaires au calcul de l'impôt (montants des revenus déclarés et situation du foyer fiscal).
                        Ces nombres, anonymes, sont ceux affichés dans les cases de l'étape 2. Ils sont ensuite envoyés 
                        au <a href="https://simulateur-ir-ifi.impots.gouv.fr/calcul_impot/2023/complet/index.htm" target="_blank" rel="noreferrer">
                        simulateur officiel des impôts</a> pour 
                        réaliser le calcul de l'impôt, et sont immédiatement supprimés une fois le calcul terminé.
                    </p>
                    <p>
                        Aucune information personnelle n'est extraite des fichiers PDF.
                    </p>
                </div>
            </div>
            </div>
        </div>
    </div>