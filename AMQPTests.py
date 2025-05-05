import requests
import pika
import socket
from base64 import b64encode
import ssl
from datetime import datetime
import threading
import logging

class AMQPTester:
    def __init__(self, host, amqp_port):
        self.host = host
        self.amqp_port = amqp_port
        self.mgmt_port = 15672
        self.concurrent_connections = 100
        self.results = []
        self.ssl_enabled = False
        self.anonymous_access = False
        self.valid_creds = None
        self.default_creds = [
            ('guest', 'guest'),
            ('admin', 'admin'),
            ('guest', 'admin'),
            ('admin', 'guest')
        ]
        logging.getLogger('pika').setLevel(logging.WARNING)

    def insert_result(self, test, vulne, detail):
        self.results.append({
            "protocol": "AMQP",
            "test": test,
            "vulne": vulne,
            "detail": detail
        })

    def check_ssl(self):
        try:
            context = ssl._create_unverified_context()
            with socket.create_connection((self.host, 5671)) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    self.ssl_enabled = True
                    cert = ssock.getpeercert()
                    self.insert_result("SSL Activation", False, "Connexion SSL réussie – SSL est activé.")

                    issuer = cert.get('issuer', [])
                    if issuer and 'CN' in issuer[0] and issuer[0][0][1] == 'localhost':
                        self.insert_result("Certificat Autosigné", True, "Certificat autosigné détecté.")

                    not_after = cert.get('notAfter')
                    if not_after:
                        cert_expiration = datetime.strptime(not_after, '%b %d %H:%M:%S %Y GMT')
                        if cert_expiration < datetime.utcnow():
                            self.insert_result("Certificat Expiré", True, "Certificat SSL expiré.")
        except Exception as e:
            self.insert_result("SSL Activation", True, f"SSL non activé ou échec de connexion : {e}")

    def scan_ports(self):
        open_ports = []
        for port in [self.amqp_port, self.mgmt_port]:
            try:
                with socket.create_connection((self.host, port), timeout=2):
                    open_ports.append(port)
            except Exception:
                continue
        self.insert_result("Port Scan", len(open_ports) > 0, f"Ports ouverts : {open_ports}" if open_ports else "Aucun port ouvert.")

    def check_anonymous_access(self):
        try:
            pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.anonymous_access = True
            self.insert_result("Connexion Anonyme", True, "Connexion AMQP anonyme réussie (⚠️ INSECURE)")
        except Exception:
            self.anonymous_access = False
            self.insert_result("Connexion Anonyme", False, "Connexion AMQP anonyme bloquée (✅ OK)")

    def bruteforce_login(self):
        if self.anonymous_access:
            self.insert_result("Bruteforce Login", True, "Connexion anonyme active – bruteforce inutile.")
            return
        for username, password in self.default_creds:
            creds = b64encode(f"{username}:{password}".encode()).decode()
            headers = {'Authorization': f'Basic {creds}'}
            try:
                r = requests.get(f"http://{self.host}:{self.mgmt_port}/api/overview", headers=headers, timeout=3)
                if r.status_code == 200:
                    self.valid_creds = (username, password)
                    self.insert_result("Bruteforce Login", True, f"Identifiants valides : {username}:{password}")
                    return
            except Exception:
                continue
        self.insert_result("Bruteforce Login", False, "Aucun identifiant par défaut valide trouvé.")

    def test_advanced_access(self):
        if not self.anonymous_access and not self.valid_creds:
            self.insert_result("Tests Avancés", False, "Pas d'accès valide pour tests avancés.")
            return

        params = pika.ConnectionParameters(self.host) if self.anonymous_access else pika.ConnectionParameters(
            self.host, credentials=pika.PlainCredentials(*self.valid_creds)
        )

        try:
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.queue_declare(queue='test_queue', durable=False)
            conn.close()
            self.insert_result("Accès VHost", True, "Accès au vhost '/' réussi.")
        except Exception as e:
            self.insert_result("Accès VHost", False, f"Échec vhost : {e}")

        try:
            url = f"http://{self.host}:{self.mgmt_port}/"
            headers = {}
            if self.valid_creds:
                creds = b64encode(f"{self.valid_creds[0]}:{self.valid_creds[1]}".encode()).decode()
                headers['Authorization'] = f'Basic {creds}'
            r = requests.get(url, headers=headers, timeout=3)
            if r.status_code == 200:
                self.insert_result("Interface de gestion accessible", True, f"Interface de gestion accessible à {url}.")
            else:
                self.insert_result("Interface de gestion accessible", False, f"HTTP {r.status_code}.")
        except Exception as e:
            self.insert_result("Interface de gestion accessible", False, f"Erreur : {e}")

        try:
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.basic_publish(exchange='', routing_key='test_queue', body='test')
            conn.close()
            self.insert_result("Publication AMQP", True, "Message publié avec succès.")
        except Exception as e:
            self.insert_result("Publication AMQP", False, f"Échec de publication : {e}")

        self.test_connection_limit(params)

    def test_connection_limit(self, params):
        failed = []
        lock = threading.Lock()

        def try_connection():
            try:
                c = pika.BlockingConnection(params)
                c.close()
            except Exception as e:
                with lock:
                    failed.append(str(e))

        threads = [threading.Thread(target=try_connection) for _ in range(self.concurrent_connections)]
        for t in threads: t.start()
        for t in threads: t.join()

        if failed:
            self.insert_result("Test Limitation Connexions", False, f"{len(failed)} échecs sur {self.concurrent_connections}. Exemple : {failed[0]}")
        else:
            self.insert_result("Test Limitation Connexions", True, f"{self.concurrent_connections} connexions réussies.")

    def run_all(self):
        self.check_ssl()
        self.scan_ports()
        self.check_anonymous_access()
        self.bruteforce_login()
        self.test_advanced_access()
        return self.results

# Test direct
if __name__ == "__main__":
    tester = AMQPTester('localhost', 5672)
    report = tester.run_all()
    for r in report:
        print(r)
