from pymodbus.client import ModbusTcpClient
import random
import time

class ModbusTester:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.results = []

    def insert_result(self, test, vulne, detail):
        self.results.append({
            "protocol": "MODBUS",  
            "test": test,
            "vulne": vulne,
            "detail": detail
        })

    def test_connection(self):
        client = ModbusTcpClient(self.host, port=self.port)
        if client.connect():
            self.insert_result("Connexion Modbus", True, "Connexion réussie (Modbus actif).")
        else:
            self.insert_result("Connexion Modbus", False, "Échec de la connexion (port fermé ou service indisponible).")
        client.close()

    def test_known_register_read(self):
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        response = client.read_holding_registers(address=9, count=1)
        if not response.isError():
            self.insert_result("Lecture registre connu", True, f"Lecture possible à l'adresse 9 : {response.registers[0]}")
        else:
            self.insert_result("Lecture registre connu", False, "Lecture échouée à l'adresse 9.")
        client.close()

    def test_bruteforce_registers(self, start=0, end=30):
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        readable = []
        for reg in range(start, end + 1):
            response = client.read_holding_registers(address=reg, count=1)
            if not response.isError():
                readable.append(reg)
        count_readable = len(readable)
        total = end - start + 1

        if count_readable == 0:
            self.insert_result("Bruteforce registres", False, "Aucun registre lisible dans la plage 0–30.")
        elif count_readable == total:
            self.insert_result("Bruteforce registres", True, "Tous les registres 0–30 sont lisibles (accès complet non restreint).")
        else:
            self.insert_result("Bruteforce registres", True, f"{count_readable}/{total} registres lisibles dans la plage 0–30 (accès partiel).")
        client.close()

    def test_register_write(self):
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        response = client.write_register(10, 12345)
        if not response.isError():
            self.insert_result("Écriture registre", True, "Écriture autorisée sur registre 10 (risque d'altération).")
        else:
            self.insert_result("Écriture registre", False, "Écriture refusée sur registre 10.")
        client.close()

    def test_flood_read(self, attempts=50):
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        success, failure = 0, 0

        for _ in range(attempts):
            reg = random.randint(0, 50)
            response = client.read_holding_registers(address=reg, count=1)
            if not response.isError():
                success += 1
            else:
                failure += 1
            time.sleep(0.01)

        rate_success = (success / attempts) * 100
        if rate_success > 90:
            detail = f"{success}/{attempts} lectures réussies ({rate_success:.1f}%). Le serveur semble tolérer un flood sans limitation."
            self.insert_result("Flood lecture rapide", True, detail)
        else:
            detail = f"{success}/{attempts} lectures réussies ({rate_success:.1f}%). Le serveur limite ou refuse les requêtes trop fréquentes."
            self.insert_result("Flood lecture rapide", False, detail)
        client.close()

    def test_out_of_bounds_access(self, start=5000, end=5010):
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        accessible = []
        for reg in range(start, end + 1):
            response = client.read_holding_registers(address=reg, count=1)
            if not response.isError():
                accessible.append(reg)
        total = end - start + 1
        count_ok = len(accessible)

        if count_ok == 0:
            self.insert_result("Accès hors plage", False, "Aucun registre hors plage accessible (5000–5010).")
        elif count_ok == total:
            self.insert_result("Accès hors plage", True, "Tous les registres 5000–5010 sont accessibles (mauvaise restriction de plage).")
        else:
            self.insert_result("Accès hors plage", True, f"{count_ok}/{total} registres hors plage accessibles (5000–5010).")
        client.close()

    def run_all(self):
        self.test_connection()
        self.test_known_register_read()
        self.test_bruteforce_registers()
        self.test_register_write()
        self.test_flood_read()
        self.test_out_of_bounds_access()
        return self.results

# Exécution autonome
# if __name__ == "__main__":
#     scanner = ModbusTester('localhost', 5020)
#     report = scanner.run_all()
#     for r in report:
#         print(r)
