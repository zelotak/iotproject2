import requests
import pika
import socket
from base64 import b64encode

RABBITMQ_HOST = 'localhost'
AMQP_PORT = 5672
MGMT_PORT = 15672
DEFAULT_CREDS = [('guest', 'guest'), ('admin', 'admin'), ('guest', 'admin'), ('admin', 'guest')]

def run_amqp_tests():
    results = []
    protocol = "AMQP"

    # Test 1 - Port scan
    open_ports = []
    for port in [5672, 15672]:
        try:
            with socket.create_connection((RABBITMQ_HOST, port), timeout=2):
                open_ports.append(port)
        except Exception:
            continue
    vulne = len(open_ports) > 0
    results.append({
        "protocol": protocol,
        "test": "Port Scan",
        "vulne": vulne,
        "detail": f"Ports ouverts : {open_ports}" if vulne else "Aucun port ouvert détecté."
    })

    # Test 2 - Bruteforce login
    valid_creds = None
    vulne = False
    for username, password in DEFAULT_CREDS:
        creds = b64encode(f"{username}:{password}".encode()).decode()
        headers = {'Authorization': f'Basic {creds}'}
        try:
            r = requests.get(f"http://{RABBITMQ_HOST}:{MGMT_PORT}/api/overview", headers=headers, timeout=3)
            if r.status_code == 200:
                valid_creds = (username, password)
                vulne = True
                results.append({
                    "protocol": protocol,
                    "test": "Bruteforce Login",
                    "vulne": True,
                    "detail": f"Identifiants par défaut valides trouvés : {username}:{password}"
                })
                break
        except Exception:
            continue
    if not vulne:
        results.append({
            "protocol": protocol,
            "test": "Bruteforce Login",
            "vulne": False,
            "detail": "Aucun identifiant par défaut valide trouvé."
        })

    # Test 3 - Anonymous AMQP connect
    try:
        pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        vulne = True
        detail = "Connexion AMQP anonyme réussie (⚠️ INSECURE)"
    except Exception:
        vulne = False
        detail = "Connexion AMQP anonyme bloquée (✅ OK)"
    results.append({
        "protocol": protocol,
        "test": "Connexion Anonyme",
        "vulne": vulne,
        "detail": detail
    })

    # Tests avancés si creds valides
    if valid_creds:
        creds = pika.PlainCredentials(*valid_creds)

        # Test 4 - Access vhost /
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=creds))
            ch = conn.channel()
            ch.queue_declare(queue='test_queue', durable=False)
            conn.close()
            vulne = True
            detail = "Accès autorisé au vhost '/' avec identifiants par défaut."
        except Exception as e:
            vulne = False
            detail = f"Accès refusé au vhost '/' : {e}"
        results.append({
            "protocol": protocol,
            "test": "Accès VHost par Défaut",
            "vulne": vulne,
            "detail": detail
        })

        # Test 5 - Federation plugin exposure
        try:
            r = requests.get(f"http://{RABBITMQ_HOST}:{MGMT_PORT}/api/federation-links", timeout=3)
            if r.status_code == 200:
                vulne = True
                detail = "API Federation accessible (risque de fuite d'infos)"
            else:
                vulne = False
                detail = "API Federation inaccessible (OK)"
        except Exception:
            vulne = False
            detail = "Erreur lors de la requête à l'API Federation."
        results.append({
            "protocol": protocol,
            "test": "API Federation Exposure",
            "vulne": vulne,
            "detail": detail
        })

        # Test 6 - Publish sans auth
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            ch = conn.channel()
            ch.basic_publish(exchange='', routing_key='test_queue', body='test')
            conn.close()
            vulne = True
            detail = "Publication sans authentification réussie (🚨 CRITICAL)"
        except Exception:
            vulne = False
            detail = "Impossible de publier sans authentification (OK)"
        results.append({
            "protocol": protocol,
            "test": "Publication sans Auth",
            "vulne": vulne,
            "detail": detail
        })
    else:
        results.append({
            "protocol": protocol,
            "test": "Tests Avancés",
            "vulne": False,
            "detail": "Tests avancés non effectués – aucun identifiant valide trouvé."
        })

    return results


# Test direct
if __name__ == "__main__":
    report = run_amqp_tests()
    for r in report:
        print(r)
