from opcua import Client

# Définir les valeurs cibles exactes pour NodeId et Name
target_nodeids = [
    "StringNodeId(ns=3;s=1023)",
    "StringNodeId(ns=3;s=1024)",
    "StringNodeId(ns=3;s=1025)",
    "StringNodeId(ns=3;s=aRMS)",
    "StringNodeId(ns=3;s=1030)"
]

target_names = [
    "QualifiedName(3:1023)",
    "QualifiedName(3:1024)",
    "QualifiedName(3:1025)",
    "QualifiedName(3:aRMS)",
    "QualifiedName(3:1030)"
]

# Adresse du serveur OPC UA
SERVER_URL = "opc.tcp://localhost:50000"
client = Client(SERVER_URL)

client.connect()

def find_matching_nodes(node):
    try:
        nodeid_str = str(node.nodeid)
        name_str = str(node.get_browse_name())
        # Si le NodeId ou le Name correspond exactement aux valeurs cibles (match direct avec "contain" sur la chaîne complète)
        if nodeid_str in target_nodeids or name_str in target_names:
            # Afficher le NodeId et le Name
            print(f"NodeId: {nodeid_str}, Name: {name_str}")
            
            # Récupérer et afficher les attributs supplémentaires du nœud
            description = node.get_description()  # Description du nœud
            datatype = node.get_data_type()  # Type de données du nœud
            access_level = node.get_access_level()  # Niveau d'accès du nœud
            value_rank = node.get_value_rank()  # Rang de valeur du nœud
            
            print(f"Description: {description}")
            print(f"DataType: {datatype}")
            print(f"AccessLevel: {access_level}")
            print(f"ValueRank: {value_rank}")
        
        # Explorer récursivement les enfants du nœud
        for child in node.get_children():
            find_matching_nodes(child)
    except Exception as e:
        print(f"Erreur pour le nœud {str(node.nodeid)}: {e}")

# Obtenir le nœud racine
root = client.get_root_node()

# Explorer toute l'arborescence et afficher uniquement les nœuds correspondant aux valeurs cibles avec leurs attributs
find_matching_nodes(root)

client.disconnect()
