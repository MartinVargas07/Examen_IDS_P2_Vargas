from flask import Flask, request, jsonify
import uuid 
import random 
import time 
from .security import token_required
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

app = Flask(__name__)

solicitudes_db = {}

class SoapCallFailedError(Exception):
    pass

@retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(SoapCallFailedError),
    reraise=True
)
def llamar_sistema_soap_externo_con_retry(solicitud_data):
    print(f"INFO: Intentando llamada a sistema SOAP para datos: {solicitud_data}")
    time.sleep(random.uniform(0.2, 0.8))
    if random.random() < 0.5: 
        print("ERROR: Llamada SOAP simulada: FALLO")
        raise SoapCallFailedError("El servicio SOAP simulado no respondió correctamente o está temporalmente inaccesible.")
    else:
        print("INFO: Llamada SOAP simulada: ÉXITO")
        return True

@app.route('/solicitudes', methods=['POST'])
@token_required
def crear_solicitud():
    print("INFO: Recibida solicitud POST en /solicitudes")
    data = request.get_json()

    if not data or 'tipo_solicitud' not in data or 'detalle' not in data:
        print("WARN: Solicitud POST inválida - Faltan datos")
        return jsonify({"message": "Datos incompletos. 'tipo_solicitud' y 'detalle' son requeridos."}), 400

    solicitud_id = str(uuid.uuid4())
    
    soap_data_simulada = {
        "id_estudiante": data.get("id_estudiante", "ID_NO_PROPORCIONADO"), 
        "tipo_tramite": data.get("tipo_solicitud")
    }
    
    estado_final_solicitud = "Error Interno Desconocido"

    try:
        print(f"INFO: Procesando creación de solicitud para tipo: {data.get('tipo_solicitud')}")
        soap_call_successful = llamar_sistema_soap_externo_con_retry(soap_data_simulada)
        
        if soap_call_successful:
            estado_final_solicitud = "Procesado"
        else:
            estado_final_solicitud = "En Revisión (Fallo no especificado en SOAP)"

    except SoapCallFailedError as e:
        print(f"ERROR: La llamada al sistema SOAP falló después de los reintentos: {e}")
        estado_final_solicitud = "En Revisión (Fallo comunicación con sistema externo)"
    except Exception as e: 
        print(f"CRITICAL: Error inesperado durante la creación de la solicitud {solicitud_id}: {e}")
        estado_final_solicitud = "Error Interno General (Consulte logs)"

    nueva_solicitud = {
        "id": solicitud_id,
        "tipo_solicitud": data["tipo_solicitud"],
        "detalle": data["detalle"],
        "id_estudiante": data.get("id_estudiante"),
        "estado": estado_final_solicitud, 
        "fecha_creacion": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    solicitudes_db[solicitud_id] = nueva_solicitud
    
    print(f"INFO: Solicitud {solicitud_id} creada con estado: {estado_final_solicitud}")
    return jsonify(nueva_solicitud), 201

@app.route('/solicitudes/<string:id_solicitud>', methods=['GET'])
@token_required
def obtener_solicitud(id_solicitud):
    print(f"INFO: Recibida solicitud GET en /solicitudes/{id_solicitud}")
    solicitud = solicitudes_db.get(id_solicitud)
    
    if solicitud:
        print(f"INFO: Solicitud {id_solicitud} encontrada.")
        return jsonify(solicitud), 200
    else:
        print(f"WARN: Solicitud {id_solicitud} NO encontrada.")
        return jsonify({"message": "Solicitud no encontrada"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    print("INFO: Health check solicitado.")
    return jsonify({
        "status": "UP", 
        "message": "Servicio de Solicitudes Estudiantiles está operativo."
    }), 200
    
if __name__ == "__main__" or __name__ == "app.main":
    from .security import generate_test_token # <--- CORREGIDO: Import relativo explícito
    
    print("--- INICIANDO SERVICIO DE SOLICITUDES (Servidor de Desarrollo Flask) ---")
    print(f"Escuchando en http://0.0.0.0:5001")
    print("Endpoints disponibles:")
    print("  POST /solicitudes         (Requiere JWT)")
    print("  GET  /solicitudes/<id>    (Requiere JWT)")
    print("  GET  /health              (No requiere JWT)")
    print("\nPara probar los endpoints protegidos, necesitarás un token JWT.")
    print("Puedes generar uno ejecutando desde la carpeta 'SolicitudService':")
    print("  python app/security.py")
    print("\nToken de prueba generado al inicio del servidor (válido 1 hora):")
    print(f"  Bearer {generate_test_token('test_user_server_startup')}\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
