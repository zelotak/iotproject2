from opcua import Client
from opcua import ua
import logging

class OPCUATester:
    def __init__(self, host, port):
        self.server_url = f'opc.tcp://{host}:{port}'
        self.results = []
        logging.getLogger('opcua').setLevel(logging.WARNING)

    def insert_result(self, test, vulne, detail):
        self.results.append({
            "protocol": "OPCUA",
            "test": test,
            "vulne": vulne,
            "detail": detail
        })

    def test_insecure_connection(self):
        client = Client(self.server_url)
        try:
            client.connect()
            self.insert_result(test="Connexion sans sécurité",vulne=True,detail="Connexion réussie sans certificat ni sécurité")
        except Exception as e:
            self.insert_result(test="Connexion sans sécurité",vulne=False,detail=f"Connexion échouée: {str(e)}")
        finally:
            try:
                client.disconnect()
            except:
                pass

    def test_security_policies(self):
        try:
            client = Client(self.server_url)
            endpoints = client.connect_and_get_server_endpoints()
            insecure_policies = []
            for ep in endpoints:
                if (
                    "None" in ep.SecurityPolicyUri
                    or ep.SecurityMode == ua.MessageSecurityMode.None_
                ):
                    insecure_policies.append({
                        "url": ep.EndpointUrl,
                        "policy": ep.SecurityPolicyUri,
                        "mode": str(ep.SecurityMode)
                    })

            if insecure_policies:
                detail = f"Politiques de sécurité faibles détectées : {insecure_policies}"
                self.insert_result(test="Vérification des politiques de sécurité",vulne=True,detail=detail)
            else:
                self.insert_result(test="Vérification des politiques de sécurité",vulne=False,detail="Aucune politique de sécurité faible détectée")
                self.insert_result("Tests Avancés", False, "Pas d'accès valide pour tests avancés.")
        except Exception as e:
            self.insert_result(test="Vérification des politiques de sécurité",vulne=True,detail=f"Erreur lors de la récupération des endpoints : {str(e)}")

    def test_anonymous_auth_allowed(self):
        try:
            client = Client(self.server_url)
            endpoints = client.connect_and_get_server_endpoints()
            anonymous_found = False

            for ep in endpoints:
                for token in ep.UserIdentityTokens:
                    if token.TokenType == ua.UserTokenType.Anonymous:
                        anonymous_found = True
                        break

            if anonymous_found:
                self.insert_result(test="Authentification anonyme autorisée",vulne=True,detail="Le serveur accepte les connexions anonymes sans mot de passe"
                )
            else:
                self.insert_result(test="Authentification anonyme autorisée",vulne=False,detail="Aucun endpoint n'autorise l'authentification anonyme")
        except Exception as e:
            self.insert_result(test="Authentification anonyme autorisée",vulne=True,detail=f"Erreur lors de la détection : {str(e)}")

    def run_all(self):
        self.test_insecure_connection()
        self.test_anonymous_auth_allowed()
        self.test_security_policies()
        return self.results

# Exemple d'utilisation :
if __name__ == "__main__":
    tester = OPCUATester('localhost', 4840)
    results = tester.run_all()
    for result in results:
        print(result)
