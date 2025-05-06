from flask import Flask, request, jsonify
from flask_cors import CORS  # Importation de CORS
from IOTPentest import IOTPenTest 
import json

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes

tester = IOTPenTest()

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    network = data.get("network")
    mask = data.get("mask")

    if not network or not mask:
        return jsonify({"error": "network and mask required"}), 400

    tester.run_network_scan(network, mask)
    return jsonify({"message": "Scan terminé", "results": tester.network_results})

@app.route("/pentest", methods=["POST"])
def pentest():
    if not tester.network_results:
        return jsonify({"error": "Faites d'abord un scan réseau."}), 400

    tester.run_pentests()

    # Convertir les résultats en JSON sans échapper les caractères spéciaux
    results = {
        "mqtt": tester.mqtt_results,
        "modbus": tester.modbus_results,
        "coap": tester.coap_results,
        "opcua": tester.opcua_results,
        "amqp": tester.amqp_results,
    }

    # Utilisation de json.dumps() avec ensure_ascii=False pour gérer les accents
    response_json = json.dumps(results, ensure_ascii=False)

    # Retourner la réponse avec le bon encodage
    return response_json, 200, {'Content-Type': 'application/json; charset=UTF-8'}

@app.route("/", methods=["GET"])
def home():
    return "API Pentest IoT opérationnelle 🚀"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
