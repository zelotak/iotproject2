import asyncio
from aiocoap import *
from aiocoap.numbers.codes import Code
import socket

class CoAPTester:
    def __init__(self, target, port):
        self.TARGET = target
        self.PORT = port
        self.COAPS_PORT = 5684
        self.ROUTES = [
            "/.well-known/core", "/sensor-data", "/sensor/temp/", "/sensor/humidity/",
            "/actuator/led/", "/data/", "/status/", "/config/", "/admin/", "/debug/", "/"
        ]
        self.discovered_routes = []
        self.payload = b'{"value": 123}'
        self.results = []

    def insert_result(self, test, vulne, detail):
        self.results.append({
            "protocol": "CoAP",
            "test": test,
            "vulne": vulne,
            "detail": detail
        })

    async def test_route(self, path):
        uri = f"coap://{self.TARGET}:{self.PORT}{path}"
        try:
            context = await Context.create_client_context()
            msg = Message(code=GET, uri=uri)
            res = await asyncio.wait_for(context.request(msg).response, timeout=5)

            if res.code.is_successful():
                self.discovered_routes.append(path)
                self.insert_result("Securisation route", True, f"La route {path} est accessible sans authentification (Code: {res.code})")
            elif res.code in [Code.FORBIDDEN, Code.UNAUTHORIZED]:
                self.insert_result("Securisation route", False, f"Accès restreint pour {path} (Code: {res.code})")
        except Exception as e:
            self.insert_result("Securisation route", False, f"Erreur route {path} : {e}")

    async def test_methods_on_routes(self):
        context = await Context.create_client_context()
        methods = [PUT, POST, DELETE]
        for route in self.discovered_routes:
            for method in methods:
                uri = f"coap://{self.TARGET}:{self.PORT}{route}"
                msg = Message(code=method, uri=uri)
                if method in [PUT, POST]:
                    msg.payload = self.payload
                try:
                    res = await asyncio.wait_for(context.request(msg).response, timeout=5)
                    if res.code in [Code.CHANGED, Code.CREATED, Code.DELETED]:
                        self.insert_result(f"Test {method.name}", True, f"{method.name} autorisé sans auth sur {route}")
                    elif res.code == Code.METHOD_NOT_ALLOWED:
                        self.insert_result(f"Test {method.name}", False, f"{method.name} bloqué sur {route}")
                except Exception as e:
                    self.insert_result(f"Test {method.name}", False, f"Erreur {method.name} sur {route} : {e}")

    async def observe_routes(self):
        for route in self.discovered_routes:
            uri = f"coap://{self.TARGET}:{self.PORT}{route}"
            try:
                context = await Context.create_client_context()
                response = await context.request(Message(code=GET, uri=uri, observe=0)).response
                self.insert_result("Observation", True, f"Observation non protégée sur {uri}")
                await asyncio.sleep(1)
            except Exception as e:
                self.insert_result("Observation", False, f"Erreur d'observation {uri} : {e}")

    def test_coaps_connection(self):
        try:
            with socket.create_connection((self.TARGET, self.COAPS_PORT), timeout=5):
                self.insert_result("Connexion CoAPS", False, "Connexion CoAPS réussie (DTLS actif).")
        except Exception as e:
            self.insert_result("Connexion CoAPS", True, f"Erreur CoAPS : {e}")

    async def test_rate_limit(self, n_requests=100):
        context = await Context.create_client_context()
        for route in self.discovered_routes:
            error_count = 0
            for i in range(n_requests):
                try:
                    uri = f"coap://{self.TARGET}:{self.PORT}{route}"
                    response = await context.request(Message(code=GET, uri=uri)).response
                    if response.code in [Code.FORBIDDEN, Code.SERVICE_UNAVAILABLE]:
                        error_count += 1
                except Exception:
                    error_count += 1
                await asyncio.sleep(0.1)
            if error_count:
                self.insert_result("Rate Limit", False, f"Limitation probable sur {route} : {error_count} erreurs.")
            else:
                self.insert_result("Rate Limit", True, f"Aucune limitation détectée sur {route}")

    async def test_malicious_payload(self):
        context = await Context.create_client_context()
        payloads = [
            '{"data": "value", timestamp}',
            'A' * 100,
            '{"data": "value", "command": "ls -l"}',
            '{"data": "<script>alert(\'XSS\')</script>"}',
            '{"username": "admin\' OR 1=1 --", "password": "password123"}',
            '{"data": "value", "payload": "<div></div>"}',
        ]
        for route in self.discovered_routes:
            for p in payloads:
                uri = f"coap://{self.TARGET}:{self.PORT}{route}"
                message = Message(code=PUT, uri=uri, payload=p.encode())
                try:
                    response = await asyncio.wait_for(context.request(message).response, timeout=5)
                    if response.code not in [Code.BAD_REQUEST, Code.METHOD_NOT_ALLOWED]:
                        self.insert_result("Payload malveillant", True, f"Payload {p} accepté sur {route}")
                        break
                except Exception as e:
                    continue
            else:
                self.insert_result("Payload malveillant", False, f"Aucun payload malveillant accepté sur {route}")

    async def run_all(self):
        await asyncio.gather(*[self.test_route(r) for r in self.ROUTES])
        await self.test_methods_on_routes()
        await self.observe_routes()
        self.test_coaps_connection()
        await self.test_rate_limit()
        await self.test_malicious_payload()

    def run(self):
        asyncio.run(self.run_all())
        return self.results

# Lancement
if __name__ == "__main__":
    scanner = CoAPTester('localhost', 5683)
    report = scanner.run()
    for r in report:
        print(r)
