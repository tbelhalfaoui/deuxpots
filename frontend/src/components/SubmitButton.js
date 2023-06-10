export const SubmitButton = ({ isLoading }) => (
    <div className="text-center">
        {!isLoading && (
            <input type="submit" className="btn btn-primary" value="Lancer le calcul" />
        )}
        {isLoading && (
            <button className="btn btn-primary" type="submit" disabled>
                <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Chargement...
            </button>
        )}
    </div>
)
