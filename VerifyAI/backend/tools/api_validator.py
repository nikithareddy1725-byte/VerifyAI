import re

class ApiValidator:
    def validate(self, endpoint: str, method: str, params: dict = None, headers: dict = None) -> dict:
        url_valid = bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', endpoint))
        
        valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}
        method_valid = method.upper() in valid_methods
        
        errors = []
        if not url_valid:
            errors.append("Invalid URL format.")
        if not method_valid:
            errors.append(f"Invalid HTTP method: {method}")
            
        return {
            "endpoint": endpoint,
            "method": method.upper(),
            "valid": url_valid and method_valid,
            "errors": errors
        }
