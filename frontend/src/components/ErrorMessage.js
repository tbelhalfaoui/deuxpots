export const ErrorMessage = ({ error }) => 
    error && 
    (<div class="alert alert-danger" role="alert">
        {(error instanceof TypeError) ? "Une erreur est survenue." : (error instanceof Error) ? error.message : error}
    </div>)
