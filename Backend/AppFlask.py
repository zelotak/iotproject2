from flask import Flask, request, jsonify
from flask_cors import CORS  
from IOTPentest import IOTPenTest
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime

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
class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    protocol = db.Column(db.String(20), nullable=False)  
    target = db.Column(db.String(64), nullable=False)    
    created_at = db.Column(db.DateTime, default=db.func.now())
    score = db.Column(db.Integer)                        
    tests = db.relationship("Test", backref="scan", cascade="all, delete-orphan")
class Test(db.Model):
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)
    test = db.Column(db.String(256), primary_key=True)
    vulne = db.Column(db.Boolean, nullable=False)
    detail = db.Column(db.Text)

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

from datetime import datetime, timedelta

@app.route("/history/list", methods=["POST"])
def list_scans():
    data = request.get_json()
    username = data.get("username")
    start_str = data.get("startDate")
    end_str = data.get("endDate")

    if not username:
        return jsonify({"error": "Nom d'utilisateur requis"}), 400

    try:
        start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else None
        end = datetime.strptime(end_str, "%Y-%m-%d") if end_str else None
    except ValueError:
        return jsonify({"error": "Format de date invalide (attendu: YYYY-MM-DD)"}), 400

    query = Scan.query.filter_by(username=username)
    if start:
        query = query.filter(Scan.created_at >= start)
    if end:
        query = query.filter(Scan.created_at <= end + timedelta(days=1))

    scans = query.order_by(Scan.created_at.desc()).all()

    result = [
        {
            "id": s.id,
            "username": s.username,
            "protocol": s.protocol,
            "target": s.target,
            "score": s.score,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in scans
    ]

    return jsonify({"scans": result}), 200

@app.route("/history/details", methods=["POST"])
def scan_details():
    data = request.get_json()
    scan_id = data.get("id")

    if not scan_id:
        return jsonify({"error": "Scan ID manquant"}), 400

    scan = Scan.query.get(scan_id)
    if not scan:
        return jsonify({"error": "Scan introuvable"}), 404

    details = [
        {
            "test": t.test,
            "vulne": t.vulne,
            "detail": t.detail
        }
        for t in scan.tests
    ]

    return jsonify({
        "score": scan.score,
        "tests": details
    }), 200

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
    tester.reset_results()
    
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

    scan_ids = []

    # Insertion des résultats dans la base de donnée 
    for proto_name, proto_results in results.items():
        if not proto_results:
            continue # On passe si pas de résultats

        # Extraire les tests et le score final
        *tests, score_entry = proto_results
        score = score_entry.get("score", 0)

        # Déterminer la cible (host:port) depuis le résultat réseau
        target = "inconnu"
        for s in tester.network_results:
            if s["protocol"].lower() == proto_name:
                target = f"{s['host']}:{s['port']}"
                break

        # Création d'une ligne de Scan
        scan = Scan(
            username=username,
            protocol=proto_name.upper(),
            target=target,
            score=score
        )
        db.session.add(scan)
        db.session.flush() # Ici la base attribue un ID à `scan`
        scan_ids.append(scan.id)  # on stocke l’identifiant du Scan créé

        for result in tests:
            test_entry = Test(
                scan_id=scan.id,    
                test=result["test"],        
                vulne=result["vulne"],        
                detail=result["detail"]        
            )
            db.session.add(test_entry)

    db.session.commit()

    # Construction d'une réponse structurée incluant les IDs
    return jsonify({
        "message": "Pentest terminé",
        "results": results,
        "scan_ids": scan_ids
    }), 200

# Route d'accueil
@app.route("/", methods=["GET"])
def home():
    return "API Pentest IoT opérationnelle 🚀"

# Créer la base de données et les tables (si elles n'existent pas déjà)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
