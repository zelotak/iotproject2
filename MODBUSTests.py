from pymodbus.client import ModbusTcpClient
import random
import time

def run_modbus_tests(host="localhost", port=5020):
    results = []
    protocol = "MODBUS"

    # Test 1 - Connexion
    client = ModbusTcpClient(host, port=port)
    if client.connect():
        vulne = True
        detail = "Connexion réussie (Modbus actif)."
    else:
        vulne = False
        detail = "Échec de la connexion (port fermé ou service indisponible)."
    results.append({
        "protocol": protocol,
        "test": "Connexion Modbus",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    # Test 2 - Lecture registre simple
    client.connect()
    response = client.read_holding_registers(address=9, count=1)
    if not response.isError():
        vulne = True
        detail = f"Lecture possible à l'adresse 9 : {response.registers[0]}"
    else:
        vulne = False
        detail = "Lecture échouée à l'adresse 9."
    results.append({
        "protocol": protocol,
        "test": "Lecture registre connu",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    # Test 3 - Bruteforce registre
    client.connect()
    readable = []
    total = 31  # plage 0 à 30 incluse

    for reg in range(total):
        response = client.read_holding_registers(address=reg, count=1)
        if not response.isError():
            readable.append(reg)

    count_readable = len(readable)

    if count_readable == 0:
        vulne = False
        detail = "Aucun registre lisible dans la plage 0–30."
    elif count_readable == total:
        vulne = True
        detail = "Tous les registres 0–30 sont lisibles (accès complet non restreint)."
    else:
        vulne = True
        detail = f"{count_readable}/{total} registres lisibles dans la plage 0–30 (accès partiel)."

    results.append({
        "protocol": protocol,
        "test": "Bruteforce registres",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    # Test 4 - Écriture sur registre
    client.connect()
    write_result = client.write_register(10, 12345)
    if not write_result.isError():
        vulne = True
        detail = "Écriture autorisée sur registre 10 (risque d'altération)."
    else:
        vulne = False
        detail = "Écriture refusée sur registre 10."
    results.append({
        "protocol": protocol,
        "test": "Écriture registre",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    # Test 5 - Flood rapide
    client.connect()
    success, failure = 0, 0
    nb_attempts = 50

    for _ in range(nb_attempts):
        reg = random.randint(0, 50)
        response = client.read_holding_registers(address=reg, count=1)
        if not response.isError():
            success += 1
        else:
            failure += 1
        time.sleep(0.01)  # Simuler un flood rapide mais modéré

    # Calcul du taux de succès
    rate_success = (success / nb_attempts) * 100
    vulne = rate_success > 90  # Si plus de 90% des requêtes passent, c'est trop permissif

    if vulne:
        detail = f"{success}/{nb_attempts} lectures réussies (taux {rate_success:.1f}%). Le serveur semble tolérer un flood sans limitation."
    else:
        detail = f"{success}/{nb_attempts} lectures réussies (taux {rate_success:.1f}%). Le serveur limite ou refuse les requêtes trop fréquentes."

    results.append({
        "protocol": protocol,
        "test": "Flood lecture rapide",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    # Test 6 - Lecture registres hors plage
    client.connect()
    hors_plage_ok = []
    plage = range(5000, 5011)  # Plage de 5000 à 5010

    for reg in plage:
        response = client.read_holding_registers(address=reg, count=1)
        if not response.isError():
            hors_plage_ok.append(reg)

    count_ok = len(hors_plage_ok)
    total = len(plage)

    if count_ok == 0:
        vulne = False
        detail = "Aucun registre hors plage accessible (5000–5010)."
    elif count_ok == total:
        vulne = True
        detail = "Tous les registres 5000–5010 sont accessibles (mauvaise restriction de plage)."
    else:
        vulne = True
        detail = f"{count_ok}/{total} registres hors plage accessibles (5000–5010)."

    results.append({
        "protocol": protocol,
        "test": "Accès hors plage",
        "vulne": vulne,
        "detail": detail
    })
    client.close()

    return results  # N'oublie pas de retourner les résultats !

# Test standalone
if __name__ == "__main__":
    report = run_modbus_tests()
    for entry in report:
        print(entry)
