import asyncio
from aiocoap import *
from aiocoap.numbers.codes import Code
import socket

TARGET = "localhost"
PORT = 5683
COAPS_PORT = 5684

ROUTES = [
    "/.well-known/core", "/sensor-data", "/sensor/temp/", "/sensor/humidity/",
    "/actuator/led/", "/data/", "/status/", "/config/", "/admin/", "/debug/", "/"
]

discovered_routes = []

payload = b'{"value": 123}'

results = {
    'routes': [],
    'methods': {},
    'authentification': 'Non activée',
    'observation': '',
    'coaps_connection': '',
    'rate_limit': '',
    'malicious_payload': []
}

async def test_route(path):
    uri = f"coap://{TARGET}:{PORT}{path}"
    try:
        context = await Context.create_client_context()
        msg = Message(code=GET, uri=uri)
        res = await asyncio.wait_for(context.request(msg).response, timeout=5)

        if res.code.is_successful():
            discovered_routes.append(path)
            results['routes'].append({
                "protocol": "CoAP",
                "test": f"Route {path} accessible sans authentification",
                "vulne": True,
                "detail": f"La route existe et est accessible sans authentification (Code: {res.code})"
            })
        elif res.code == Code.NOT_FOUND:
            pass
        elif res.code == Code.FORBIDDEN:
            results['authentification'] = 'Activée sur au moins une route'
            results['routes'].append({
                "protocol": "CoAP",
                "test": f"Route {path} nécessite une authentification",
                "vulne": False,
                "detail": f"Accès interdit à la route (Code: {res.code})"
            })
        elif res.code == Code.UNAUTHORIZED:
            results['authentification'] = 'Activée sur au moins une route'
            results['routes'].append({
                "protocol": "CoAP",
                "test": f"Route {path} nécessite une authentification",
                "vulne": False,
                "detail": f"Authentification requise (Code: {res.code})"
            })
        else:
            results['routes'].append({
                "protocol": "CoAP",
                "test": f"Route {path} résultat inconnu",
                "vulne": False,
                "detail": f"Code inconnu (Code: {res.code})"
            })
    except Exception as e:
        results['routes'].append({
            "protocol": "CoAP",
            "test": f"Route {path} erreur",
            "vulne": False,
            "detail": f"Erreur lors du test de la route : {e}"
        })

async def test_methods_on_discovered_routes():
    context = await Context.create_client_context()
    methods_to_test = [PUT, POST, DELETE]

    for route in discovered_routes:
        for method in methods_to_test:
            uri = f"coap://{TARGET}:{PORT}{route}"
            msg = Message(code=method, uri=uri)
            if method in [PUT, POST]:
                msg.payload = payload

            try:
                res = await asyncio.wait_for(context.request(msg).response, timeout=5)

                # Vérification simplifiée du code de réponse pour chaque méthode
                if res.code == Code.CHANGED:  # Code 2.04 pour PUT
                    results['methods'][f"{method.name} on {route}"] = {
                        "protocol": "CoAP",
                        "test": f"Méthode {method.name} sur {route}",
                        "vulne": True,
                        "detail": f"Vulnérabilité détectée : {method.name} permise sans authentification ou validation (Code: {res.code})"
                    }
                elif res.code == Code.CREATED:  # Code 2.01 pour POST
                    results['methods'][f"{method.name} on {route}"] = {
                        "protocol": "CoAP",
                        "test": f"Méthode {method.name} sur {route}",
                        "vulne": True,
                        "detail": f"Vulnérabilité détectée : {method.name} permise sans authentification ou validation (Code: {res.code})"
                    }
                elif res.code == Code.DELETED:  # Code 2.02 pour DELETE
                    results['methods'][f"{method.name} on {route}"] = {
                        "protocol": "CoAP",
                        "test": f"Méthode {method.name} sur {route}",
                        "vulne": True,
                        "detail": f"Vulnérabilité détectée : {method.name} permise sans authentification ou validation (Code: {res.code})"
                    }
                elif res.code == Code.METHOD_NOT_ALLOWED:  # Code 4.05 (Méthode non autorisée)
                    results['methods'][f"{method.name} on {route}"] = {
                        "protocol": "CoAP",
                        "test": f"Méthode {method.name} sur {route}",
                        "vulne": False,
                        "detail": f"Aucune vulnérabilité détectée : {method.name} non autorisée sur cette route (Code: {res.code})"
                    }
                else:
                    # Autres codes de réponse non attendus
                    results['methods'][f"{method.name} on {route}"] = {
                        "protocol": "CoAP",
                        "test": f"Méthode {method.name} sur {route}",
                        "vulne": False,
                        "detail": f"Réponse inattendue ou erreur lors du test de {method.name}: {res.code}"
                    }
            except Exception as e:
                results['methods'][f"{method.name} on {route}"] = {
                    "protocol": "CoAP",
                    "test": f"Méthode {method.name} sur {route} échec",
                    "vulne": False,
                    "detail": f"Erreur lors du test de la méthode {method.name}: {e}"
                }

async def observe_route():
    for route in discovered_routes:
        uri = f"coap://{TARGET}:{PORT}{route}"
        try:
            context = await Context.create_client_context()
            response = await context.request(Message(code=GET, uri=uri, observe=0)).response
            results['observation'] = {
                "protocol": "CoAP",
                "test": f"Observation sur {uri}",
                "vulne": True,
                "detail": f"Vulnérabilité détectée : Observation non protégée sur {uri} - Payload: {response.payload.decode()}"
            }
            await asyncio.sleep(1)
        except Exception as e:
            results['observation'] = {
                "protocol": "CoAP",
                "test": f"Observation sur {uri} échec",
                "vulne": False,
                "detail": f"Erreur lors de l'observation : {e}"
            }

def test_coaps_connection():
    try:
        with socket.create_connection((TARGET, COAPS_PORT), timeout=5):
            results['coaps_connection'] = {
                "protocol": "CoAPS",
                "test": "Connexion CoAPS",
                "vulne": False,
                "detail": f"Connexion réussie à {TARGET}:{COAPS_PORT} - CoAPS activé avec DTLS."
            }
    except Exception as e:
        results['coaps_connection'] = {
            "protocol": "CoAPS",
            "test": "Connexion CoAPS",
            "vulne": True,
            "detail": f"Erreur lors de la connexion à {TARGET}:{COAPS_PORT}: {e} - Aucun CoAPS activé avec DTLS."
        }

async def test_rate_limit(n_requests):
    context = await Context.create_client_context()
    error_count = 0

    for route in discovered_routes:
        for i in range(n_requests):
            try:
                uri = f"coap://{TARGET}:{PORT}{route}"
                response = await context.request(Message(code=GET, uri=uri)).response

                if response.code in [Code.FORBIDDEN, Code.SERVICE_UNAVAILABLE]:
                    results['rate_limit'] = {
                        "protocol": "CoAP",
                        "test": f"Limitation de débit sur {route}",
                        "vulne": False,
                        "detail": f"Limite de débit probable : Requête {i+1} a renvoyé {response.code}"
                    }
                    error_count += 1
            except Exception as e:
                error_count += 1
                results['rate_limit'] = {
                    "protocol": "CoAP",
                    "test": f"Limitation de débit sur {route}",
                    "vulne": False,
                    "detail": f"Erreur requête {i+1}: {e}"
                }
            await asyncio.sleep(0.1)

    if error_count > 0:
        results['rate_limit'] = {
            "protocol": "CoAP",
            "test": "Rate limit",
            "vulne": False,
            "detail": "Le serveur pourrait appliquer un rate limit."
        }
    else:
        results['rate_limit'] = {
            "protocol": "CoAP",
            "test": "Rate limit",
            "vulne": True,
            "detail": "Aucun rate limit détecté après les requêtes."
        }

async def test_malicious_payload():
    context = await Context.create_client_context()
    malicious_payloads = [
        '{"data": "value", timestamp}',
        'A' * 100,
        '{"data": "value", "command": "ls -l"}',
        '{"data": "<script>alert(\'XSS\')</script>"}',
        '{"username": "admin\' OR 1=1 --", "password": "password123"}',
        '{"data": "value", "payload": "<div></div>"}',
    ]

    for route in discovered_routes:
        # Variable pour vérifier si une vulnérabilité a été détectée
        is_vulnerable = False
        
        for malicious_payload in malicious_payloads:
            uri = f"coap://{TARGET}:{PORT}{route}"
            message = Message(code=PUT, uri=uri, payload=malicious_payload.encode('utf-8'))
            try:
                response = await asyncio.wait_for(context.request(message).response, timeout=5)

                # Si une vulnérabilité est détectée (réponse inattendue, comme un code 2.04 ou similaire)
                if response.code != Code.BAD_REQUEST and response.code != Code.METHOD_NOT_ALLOWED:
                    is_vulnerable = True
                    results['malicious_payload'].append({
                        'protocol': 'CoAP',
                        'test': f'Payload malveillant sur {route}',
                        'vulne': True,
                        'detail': f'Payload malveillant envoyé : {malicious_payload} - Réponse: {response.code}'
                    })
                    break  # Arrête les tests de payloads dès qu'une vulnérabilité est détectée

            except asyncio.TimeoutError:
                results['malicious_payload'].append({
                    'protocol': 'CoAP',
                    'test': f'Payload malveillant sur {route}',
                    'vulne': False,
                    'detail': f'Payload malveillant envoyé : {malicious_payload} - Timeout'
                })
            except Exception as e:
                results['malicious_payload'].append({
                    'protocol': 'CoAP',
                    'test': f'Payload malveillant sur {route}',
                    'vulne': False,
                    'detail': f'Payload malveillant envoyé : {malicious_payload} - Erreur: {e}'
                })

        # Si aucune vulnérabilité n'est détectée après avoir testé tous les payloads
        if not is_vulnerable:
            results['malicious_payload'].append({
                'protocol': 'CoAP',
                'test': f'Payload malveillant sur {route}',
                'vulne': False,
                'detail': f'Pas de vulnérabilité détectée pour les payloads malveillants sur {route}'
            })


async def main():
    # Test des routes
    await asyncio.gather(*[test_route(route) for route in ROUTES])

    # Test des méthodes sur les routes découvertes
    await test_methods_on_discovered_routes()

    # Test de l'observation sur les routes découvertes
    await observe_route()

    # Test de la connexion CoAPS
    test_coaps_connection()

    # Test de la limitation de débit sur les routes découvertes
    await test_rate_limit(100)

    await test_malicious_payload()

    # Affichage des résultats
    print("\nRésultats des tests :\n")
    # Pour afficher les résultats sous forme de dictionnaire
    for key, value in results.items():
        if isinstance(value, list):
            print(f"{key}:")
            for entry in value:
                print(f"  - {entry}")
        elif isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  - {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

def run_tests():
    asyncio.run(main())

if __name__ == "__main__":
    run_tests()  