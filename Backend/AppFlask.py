from flask import Flask, request, jsonify
from flask_cors import CORS  
from IOTPentest import IOTPenTest
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/userdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'supersecretkey' 

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Définir un modèle utilisateur pour la base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

tester = IOTPenTest()

# Route pour s'enregistrer (enregistrement d'un nouvel utilisateur)
@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username et password sont requis"}), 400

    # Vérifier si l'utilisateur existe déjà
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Utilisateur déjà existant"}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    
    user = User.query.filter_by(username=username).first()
    
    # Vérifier si l'utilisateur existe et si les mots de passe correspondent
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({"message": "Connexion réussie", "is_premium": user.is_premium, "is_connected": True})
    
    return jsonify({"error": "Identifiants invalides"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Déconnexion réussie", "is_connected": False})

# Route pour réinitialiser son mot de passe 
@app.route("/reset", methods=["POST"])
def reset():
    username = request.json.get("username")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Utilisateur inconnu"}), 401
    
    return jsonify({"message": "Un email de réinitialisation été envoyé"})

# Route pour effectuer un scan de réseau (accessible seulement si l'utilisateur est connecté)
@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    username = request.json.get("username")
    mode = data.get('mode')

    # Vérifier si l'utilisateur est connecté
    if not username:
        return jsonify({"error": "Vous devez être connecté pour effectuer un scan."}), 401

    # Lancement d'un scan réseau ou host
    if mode == 'network':
        network = data.get("network")
        mask = data.get("mask")
        if not network or not mask:
            return jsonify({"error": "Réseau et masque sont requis"}), 400
        tester.run_network_scan(network, mask)
    else:
        host = data.get('host')
        if not host:
            return jsonify({"error": "L'adresse IP Hote est requise"}), 400
        tester.run_network_scan(host)

    return jsonify({"message": "Scan terminé", "results": tester.network_results})

# Route pour effectuer un pentest (accessible seulement si l'utilisateur est connecté)
@app.route("/pentest", methods=["POST"])
def pentest():
    username = request.json.get("username")
    
    # Vérifier si l'utilisateur est connecté
    if not username:
        return jsonify({"error": "Vous devez être connecté pour effectuer un pentest."}), 401

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

# Route d'accueil
@app.route("/", methods=["GET"])
def home():
    return "API Pentest IoT opérationnelle 🚀"

# Créer la base de données et les tables (si elles n'existent pas déjà)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
