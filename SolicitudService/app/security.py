import jwt
from functools import wraps
from flask import request, jsonify
import datetime # Ya importas datetime

# No necesitas 'import timezone' por separado si usas datetime.timezone

JWT_SECRET = "mi-super-secreto-jwt-para-examen" 
JWT_ALGORITHM = "HS256"

def validate_jwt_locally(token):
    try:
        # La validación de 'exp' la hace PyJWT automáticamente si está presente en el token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "payload": payload, "error": None}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "payload": None, "error": "Token ha expirado"}
    except jwt.InvalidTokenError:
        return {"valid": False, "payload": None, "error": "Token inválido"}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            else:
                return jsonify({"message": "Formato de token inválido. Usar 'Bearer <token>'"}), 401

        if not token:
            return jsonify({"message": "Token es requerido"}), 401

        validation_result = validate_jwt_locally(token)
        if not validation_result["valid"]:
            return jsonify({"message": f"Token inválido: {validation_result['error']}"}), 401
        
        return f(*args, **kwargs)
    return decorated

def generate_test_token(user_id="test_user_default_id"):
    # Usar datetime.timezone.utc que está disponible a través del módulo datetime importado
    # Esto es compatible con Python 3.2+
    utc_now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        "user_id": user_id,
        "iss": "mi-aplicacion-solicitudes", 
        "exp": utc_now + datetime.timedelta(hours=1) 
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

if __name__ == '__main__':
    test_user = "martin_vargas_07"
    generated_token = generate_test_token(test_user)
    
    print("--- Generated Test JWT Token ---")
    print(f"User ID en el token: {test_user}")
    print(f"Secret Key (usado para firmar y verificar): {JWT_SECRET}")
    print(f"Algorithm: {JWT_ALGORITHM}")
    print("\nToken JWT (válido por 1 hora):")
    print(f"Bearer {generated_token}")
    
    print("\nPayload decodificado (para referencia):")
    try:
        # Para decodificar, PyJWT también valida 'exp' por defecto si está presente.
        decoded_payload = jwt.decode(generated_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(decoded_payload)
    except Exception as e:
        print(f"Error decodificando el token para referencia: {e}")
        
    print("\nInstrucción:")
    print("Copia la línea completa que empieza con 'Bearer ' para usarla en las cabeceras")
    print("de tus solicitudes HTTP (ej. en Postman o curl).")

