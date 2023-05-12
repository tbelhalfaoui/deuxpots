export const SubmitButton = ({ isLoading }) => (
    <div class="text-center">
        {!isLoading && (
            <input type="submit" class="btn btn-primary" value="Continuer" />
        )}
        {isLoading && (
            <button class="btn btn-primary" type="submit" disabled>
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Chargement...
            </button>
        )}
    </div>
)
