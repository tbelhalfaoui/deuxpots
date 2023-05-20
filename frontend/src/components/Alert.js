export const ErrorMessage = ({ error }) => 
    error && 
    (<div class="alert alert-danger" role="alert">
        {(error instanceof TypeError) ? "Une erreur est survenue." : (error instanceof Error) ? error.message : error}
    </div>)


export const WarningMessage = ({ warning }) => 
    warning && 
    (<div class="alert alert-warning" role="alert">
        {warning}
    </div>)
