import time
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)

class MQTTTester:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.results = []

    def try_connection(self, username=None, password=None, label="Test"):
        """Essaye une connexion et retourne True si succès, False sinon"""
        client = mqtt.Client()
        if username:
            client.username_pw_set(username, password)
        
        print(f"[{label}] ➜ Connexion avec {username or 'anonyme'} / {password or 'aucun mot de passe'}")
        try:
            client.connect(self.host, self.port, 5)
            client.loop_start()
            time.sleep(2)
            connected = client.is_connected()
            client.disconnect()
            client.loop_stop()
            print(f"[{label}] ✅ RÉUSSI\n" if connected else f"[{label}] ❌ ÉCHOUÉ\n")
            return connected
        except Exception as e:
            print(f"[{label}] ❌ ÉCHOUÉ - Exception : {str(e)}\n")
            return False

    def test_authentication(self):
        print("== 🔐 TEST AUTHENTIFICATION ==")
        
        # Test de la connexion anonyme (sans mot de passe)
        anonymous = self.try_connection(label="Anonyme")
        if anonymous:
            self.results.append({
                "protocol": "MQTT",
                "test": "Connexion anonyme",
                "vulne": "Oui",  # C'est une vulnérabilité d'accepter une connexion anonyme sans mot de passe
                "detail": "Connexion réussie sans mot de passe requis"
            })
        else:
            # Test de la connexion avec un mot de passe vide
            empty_pass = self.try_connection(username="testuser", password="", label="User sans mot de passe")
            if empty_pass:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Connexion avec mot de passe vide",
                    "vulne": "Oui",  # Connexion avec mot de passe vide est une vulnérabilité
                    "detail": "Connexion réussie avec mot de passe vide"
                })
            else:
                # Test de la connexion avec un mot de passe faible
                weak_pass = self.try_connection(username="testuser", password="1234", label="Mot de passe faible")
                if weak_pass:
                    self.results.append({
                        "protocol": "MQTT",
                        "test": "Connexion avec mot de passe faible",
                        "vulne": "Oui",  # Un mot de passe faible est également une vulnérabilité
                        "detail": "Connexion réussie avec mot de passe faible"
                    })
                else:
                    self.results.append({
                        "protocol": "MQTT",
                        "test": "Mot de passe requis",
                        "vulne": "Non",  # Pas de vulnérabilité, un mot de passe est requis
                        "detail": "Connexion avec mot de passe requis, aucune vulnérabilité détectée"
                    })
                    print("⚠️ Mot de passe requis. On tente un brute force.\n")
                    valid_creds = self.test_brute_force_authentication()
                    if valid_creds:
                        self.valid_username, self.valid_password = valid_creds
                    else:
                        self.valid_username = self.valid_password = None

    def test_brute_force_authentication(self):
        print("== 🔓 TEST BRUTE FORCE ==")
        credentials_list = [
            ("admin", "password"),
            ("root", "toor"),
            ("testuser", "1234"),
            ("admin", "admin123"),
            ("mqtt", "mqtt")
        ]

        for username, password in credentials_list:
            success = self.try_connection(username, password, label=f"BruteForce: {username}")
            if success:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Brute Force",
                    "vulne": "Oui",
                    "detail": f"Identifiants valides trouvés : {username}:{password}"
                })
                return username, password

        self.results.append({
            "protocol": "MQTT",
            "test": "Brute Force",
            "vulne": "Non",
            "detail": "Aucun identifiant valide trouvé lors du brute force"
        })
        return None

    def test_authorization(self):
        print("== 🔑 TEST AUTORISATIONS PUB/SUB ==")
        topics = ["public/topic", "private/topic", "$SYS/broker"]
        
        client = mqtt.Client()
        if self.valid_username:
            client.username_pw_set(self.valid_username, self.valid_password)

        client.on_message = self.on_message

        vuln_pub = False  # Suivi de la vulnérabilité pour publication
        vuln_sub = False  # Suivi de la vulnérabilité pour abonnement

        try:
            client.connect(self.host, self.port)
            client.loop_start()
            time.sleep(1)

            # Test de publication sur n'importe quel topic
            for topic in topics:
                try:
                    result_pub = client.publish(topic, "Test MQTT").rc
                    if result_pub == 0:
                        vuln_pub = True  # Publication autorisée sur n'importe quel topic = vulnérabilité
                        break  # Si une publication réussit, on arrête le test de publication
                except Exception as e:
                    print(f"Erreur lors de la publication sur {topic}: {e}")

            # Test d'abonnement aux topics sensibles (par exemple $SYS)
            for topic in topics:
                try:
                    result_sub = client.subscribe(topic)[0]
                    if topic.startswith("$SYS"):  # Vérifie si c'est un topic sensible
                        if result_sub == 0:
                            vuln_sub = True  # Abonnement autorisé à un topic sensible = vulnérabilité
                            break  # Si on peut s'abonner à un topic sensible, on arrête le test d'abonnement
                except Exception as e:
                    print(f"Erreur lors de l'abonnement à {topic}: {e}")

            client.disconnect()
            client.loop_stop()

            # Résultats des vulnérabilités détectées
            if vuln_pub:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Vulnérabilité : Publication autorisée",
                    "vulne": "Oui",
                    "detail": "La publication est autorisée sur des topics (public, private, $SYS) sans restrictions"
                })

            if vuln_sub:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Vulnérabilité : Abonnement à un topic sensible autorisé",
                    "vulne": "Oui",
                    "detail": "L'abonnement à un topic sensible ($SYS/broker) est autorisé"
                })

        except Exception as e:
            self.results.append({
                "protocol": "MQTT",
                "test": "Authorization",
                "vulne": "Non",
                "detail": f"Erreur pendant le test d'autorisation : {e}"
            })
            return

    def on_message(self, client, userdata, msg):
        print(f"[MSG] {msg.topic} → {msg.payload.decode()}")

    def test_flood_protection(self):
        print("== 🌊 TEST PROTECTION FLOOD (DoS) ==")
        try:
            clients = [mqtt.Client(f"client_{i}") for i in range(50)]
            if self.valid_username:
                for c in clients:
                    c.username_pw_set(self.valid_username, self.valid_password)

            for c in clients:
                c.connect(self.host, self.port)
                c.loop_start()

            time.sleep(5)

            alive = sum(c.is_connected() for c in clients)

            for c in clients:
                c.disconnect()
                c.loop_stop()

            if alive < 50:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Protection flood",
                    "vulne": "Non",
                    "detail": f"Connexions actives : {alive}/50, le broker limite bien les connexions"
                })
            else:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Protection flood",
                    "vulne": "Oui",
                    "detail": f"Connexions actives : {alive}/50, le broker accepte trop de connexions"
                })
        except Exception as e:
            self.results.append({
                "protocol": "MQTT",
                "test": "Protection flood",
                "vulne": "Non",
                "detail": f"Erreur pendant le test de flood : {e}"
            })

    def test_reconnection(self):
        print("== 🔄 TEST RECONNEXION AUTOMATIQUE ==")
        client = mqtt.Client()
        if self.valid_username:
            client.username_pw_set(self.valid_username, self.valid_password)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ Connecté avec succès !")
            else:
                print(f"❌ Échec de connexion avec code {rc}")

        def on_disconnect(c, u, rc):
            print(f"💥 Déconnecté avec code {rc}")
            if rc != 0:
                print("🔁 Tentative de reconnexion...")
                try:
                    c.reconnect()
                    print("✅ Reconnexion réussie")
                except Exception as e:
                    print(f"❌ Échec de reconnexion : {e}")

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.connect(self.host, self.port)
        client.loop_start()
        time.sleep(2)
        print("💥 Déconnexion manuelle du client")
        client.disconnect()
        time.sleep(5)

        if client.is_connected():
            self.results.append({
                "protocol": "MQTT",
                "test": "Reconnexion automatique",
                "vulne": "Non",
                "detail": "Le client est reconnecté après la déconnexion."
            })
        else:
            self.results.append({
                "protocol": "MQTT",
                "test": "Reconnexion automatique",
                "vulne": "Oui",
                "detail": "Le client n'a pas réussi à se reconnecter."
            })

        client.loop_stop()

    def test_tls_connection(self):
        print("== 🔐 TEST TLS/SSL ==")
        client = mqtt.Client()
        client.tls_set()

        try:
            client.connect(self.host, 8883)
            client.loop_start()
            time.sleep(2)
            if client.is_connected():
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Connexion TLS",
                    "vulne": "Non",
                    "detail": "Connexion TLS réussie"
                })
            else:
                self.results.append({
                    "protocol": "MQTT",
                    "test": "Connexion TLS",
                    "vulne": "Oui",
                    "detail": "Connexion TLS échouée"
                })
            client.disconnect()
            client.loop_stop()
        except Exception as e:
            self.results.append({
                "protocol": "MQTT",
                "test": "Connexion TLS",
                "vulne": "Oui",
                "detail": f"Erreur TLS : {e}"
            })

# Fonction pour exécuter les tests et afficher le rapport
def run_mqtt_tests():
    mqtt_host = "localhost"
    mqtt_port = 1883
    tester = MQTTTester(mqtt_host, mqtt_port)

    tester.test_authentication()
    tester.test_authorization()
    tester.test_flood_protection()
    tester.test_reconnection()
    tester.test_tls_connection()

    return tester.results

# Test standalone
if __name__ == "__main__":
    results = run_mqtt_tests()
    for entry in results:
        print(entry)
