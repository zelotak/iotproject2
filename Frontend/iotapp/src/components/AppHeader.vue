<template>
  <div>
    <header class="app-header">
      <div class="header-content">
        <h1>IOT Pentesting</h1>
        <p class="subtitle">Analyse et test des protocoles IoT courants</p>
      </div>
      <div class="navbar">
        <ul>
          <li class="nav-tab" :class="{ active: activeTab === 'SCAN' }" @click="selectTab('SCAN')">SCAN</li>
          <li class="nav-tab" :class="{ active: activeTab === 'MQTT', disabled: !testsStarted }" @click="selectTab('MQTT')">MQTT</li>
          <li class="nav-tab" :class="{ active: activeTab === 'COAP', disabled: !testsStarted }" @click="selectTab('COAP')">COAP</li>
          <li class="nav-tab" :class="{ active: activeTab === 'MODBUS', disabled: !testsStarted }" @click="selectTab('MODBUS')">MODBUS</li>
          <li class="nav-tab" :class="{ active: activeTab === 'OPCUA', disabled: !testsStarted }" @click="selectTab('OPCUA')">OPCUA</li>
          <li class="nav-tab" :class="{ active: activeTab === 'AMQP', disabled: !testsStarted }" @click="selectTab('AMQP')">AMQP</li>
          <li class="nav-tab" :class="{ active: activeTab === 'HISTO', disabled: false}" @click="selectTab('HISTO')">HISTO</li>
          <li class="auth-button" @click="toggleAccountMenu">
            <span v-if="isLoggedIn">{{ username }}</span>
            <span v-else>Compte</span>
            <div v-if="showAccountMenu" class="account-menu">
              <template v-if="!isLoggedIn">
                <div @click="toggleLoginModal">Se connecter</div>
                <div @click="toggleRegisterModal">Créer un compte</div>
                <div @click="toggleResetModal">Mot de passe oublié</div>
              </template>
              <template v-else>
                <div>Status : <strong>{{ isPremium ? 'Premium' : 'Gratuit' }}</strong></div>
                <div v-if="!isPremium" @click="upgradeToPremium">Voir nos offres</div>
                <div @click="logout">Déconnexion</div>
              </template>
              <div @click="showTerms = true" class="cgu-link">Voir les CGU ℹ️</div>
              <div @click="ExportPDF = true" class="export-link">Exporter les résulats</div>
              <div class="contact">Contact : support@pentestiot.io</div>
            </div>
          </li>
        </ul>
      </div>
    </header>

    <!-- Modal de connexion -->
    <div v-if="showLoginModal" class="modal">
      <div class="modal-content">
        <h2>Connexion</h2>
        <input v-model="loginUsername" placeholder="Adresse mail" />
        <input v-model="loginPassword" type="password" placeholder="Mot de passe" />
        <button @click="login(loginUsername, loginPassword)">Se connecter</button>
        <button @click="closeLoginModal">Fermer</button>
      </div>
    </div>

    <!-- Modal de réinitialisation de mot de passe -->
    <div v-if="showResetModal" class="modal">
      <div class="modal-content">
        <h2>Mot de passe oublié</h2>
        <input v-model="resetUsername" placeholder="Adresse mail" />
        <button @click="reset(resetUsername)">Réinitialiser</button>
        <button @click="closeResetModal">Fermer</button>
      </div>
    </div>

    <!-- Modal d'inscription -->
    <div v-if="showRegisterModal" class="modal">
      <div class="modal-content">
        <h2>Créer un compte</h2>
        <input v-model="registerUsername" placeholder="Adresse mail" />
        <input v-model="registerPassword" type="password" placeholder="Mot de passe" />
        <button @click="register(registerUsername, registerPassword)">Créer un compte</button>
        <button @click="closeRegisterModal">Fermer</button>
      </div>
    </div>

    <!-- Modal CGU -->
    <div v-if="showTerms" class="modal">
      <div class="modal-content cgu-modal">
        <h2>Conditions Générales d'Utilisation</h2>
        <div class="cgu-content">
          <p>Dernière mise à jour : 30 juin 2025</p>

          <h3>1. Objet</h3>
          <p>PentestIoT est une plateforme dédiée à l’analyse et au test de la sécurité des protocoles IoT. En accédant au service, l’utilisateur accepte les présentes CGU.</p>

          <h3>2. Conditions d’utilisation</h3>
          <p>Ce service est destiné à des tests effectués exclusivement sur des dispositifs autorisés. Toute tentative de test sur une cible sans consentement explicite est strictement interdite.</p>

          <h3>3. Compte utilisateur</h3>
          <p>L’utilisateur est responsable de ses identifiants. Toute activité réalisée sous son compte lui est imputable.</p>

          <h3>4. Propriété intellectuelle</h3>
          <p>Le contenu de la plateforme, incluant le code, les interfaces et la documentation, est la propriété exclusive de ses créateurs.</p>

          <h3>5. Données personnelles</h3>
          <p>Seule l’adresse e-mail est collectée, et uniquement à des fins d’identification. Aucune donnée liée aux tests réalisés n’est stockée.</p>

          <h3>6. Responsabilité</h3>
          <p>PentestIoT ne peut être tenu responsable d’un usage inapproprié de ses outils. L’utilisateur est entièrement responsable des tests qu’il effectue.</p>

          <h3>7. Sécurité</h3>
          <p>Le service est fourni "en l’état". L’utilisateur est invité à protéger ses propres données et équipements lors de l’usage de la plateforme.</p>

          <h3>8. Modifications</h3>
          <p>Les présentes CGU peuvent être modifiées à tout moment. Les utilisateurs seront informés en cas de changement important.</p>

          <h3>9. Droit applicable</h3>
          <p>Les CGU sont soumises au droit français. Tout litige sera porté devant les tribunaux compétents.</p>

          <h3>10. Contact</h3>
          <p>Pour toute question : <strong>support@pentestiot.io</strong></p>
        </div>
        <button @click="showTerms = false">Fermer</button>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AppHeader',
  props: {
    scanStarted: Boolean,
    testsStarted: Boolean
  },
  data() {
    return {
      activeTab: 'SCAN',
      isLoggedIn: false,
      username: '',
      showLoginModal: false,
      showRegisterModal: false,
      showResetModal: false,
      loginUsername: '',
      loginPassword: '',
      registerUsername: '',
      registerPassword: '',
      resetUsername: '',
      showAccountMenu: false,
      isPremium: false,
      showTerms: false
    };
  },
  mounted() {
    this.checkLoginStatus();
  },
  methods: {
    selectTab(tab) {
      if (this.testsStarted || tab === 'SCAN' || tab === 'HISTO') {
        this.activeTab = tab;
        this.$emit('changeTab', tab);
      }
    },
    toggleLoginModal() {
      this.showLoginModal = true;
    },
    closeLoginModal() {
      this.showLoginModal = false;
    },
    toggleRegisterModal() {
      this.showRegisterModal = true;
    },
    closeRegisterModal() {
      this.showRegisterModal = false;
    },
    toggleResetModal() {
      this.showResetModal = true;
    },
    closeResetModal() {
      this.showResetModal = false;
    },
    toggleAccountMenu() {
      this.showAccountMenu = !this.showAccountMenu;
    },
    upgradeToPremium() {
      alert("Redirection vers la page de paiement (à implémenter)");
    },
    async login(username, password) {
      try {
        const { data } = await axios.post('http://localhost:5000/login', {
          username,
          password
        });

        if (data.is_connected) {
          localStorage.setItem('username', username);
          localStorage.setItem('isPremium', data.is_premium);
          localStorage.setItem('isConnected', 'true');

          this.isLoggedIn = true;
          this.username = username;
          this.isPremium = data.is_premium;
          this.closeLoginModal();
        } else {
          alert("Échec de la connexion");
        }
      } catch (err) {
        console.error("Erreur de connexion", err);
        alert("Identifiants invalides !");
      }
    },
    async register(username, password) {
      try {
        await axios.post('http://localhost:5000/register', { username, password });
        alert("Compte créé avec succès !");
        await this.login(username, password);
        this.closeRegisterModal();
      } catch (err) {
        console.error("Erreur d'inscription", err);
        alert("Erreur lors de l'inscription");
      }
    },
    async reset(username) {
      try {
        const response = await axios.post('http://localhost:5000/reset', { username });
        // Récupère le message depuis le backend
        const message = response.data.message;

        alert(message);
        this.closeResetModal();
      } catch (err) {
        console.error("Erreur de réinitialisation", err);
        // Si le backend renvoie une erreur avec message JSON :
        if (err.response && err.response.data && err.response.data.error) {
          alert(err.response.data.error);  // Exemple : "Utilisateur inconnu"
        } else {
          alert("Erreur lors de la réinitialisation");
        }
      }
    },
    async logout() {
      try {
        await axios.post('http://localhost:5000/logout');

        localStorage.removeItem('isConnected');
        localStorage.removeItem('isPremium');
        localStorage.removeItem('username');

        this.isLoggedIn = false;
        this.username = '';
        this.isPremium = false;

        // Recharge propre de la page
        window.location.reload();
      } catch (err) {
        console.error("Erreur lors de la déconnexion", err);
        alert("Erreur lors de la déconnexion.");
      }
    },
    checkLoginStatus() {
      const connected = localStorage.getItem('isConnected') === 'true';
      this.isLoggedIn = connected;
      if (connected) {
        this.username = localStorage.getItem('username');
        this.isPremium = localStorage.getItem('isPremium') === 'true';
      }
    }
  }
};
</script>

<style scoped>
/* Style du Header */
.app-header {
  background: linear-gradient(to right, #1e2a34, #263544); /* Dégradé subtil */
  color: #ffffff;
  padding: 20px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px; /* Espacement entre le titre et la barre de navigation */
}

h1 {
  font-size: 38px; /* Taille du titre avec plus de présence */
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.subtitle {
  font-size: 16px;
  color: #cfcfcf;
  letter-spacing: 1px;
  margin-top: 8px;
}

/* Barre de navigation */
.navbar {
  display: flex;
  justify-content: center;
  background-color: #263544;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 100%;
  padding: 10px 0;
}

.navbar ul {
  list-style-type: none;
  display: flex;
  gap: 30px;
  padding: 0;
  margin: 0;
}

/* Onglets de navigation */
.nav-tab {
  padding: 8px 18px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  background-color: #324a60;
  border-radius: 25px;
  transition: background-color 0.3s ease, transform 0.3s ease;
  color: white;
}

.nav-tab:hover:not(.disabled) {
  background-color: #2a3c52;
  transform: scale(1.1);
}

.nav-tab.active {
  background-color: #009688;
  color: white;
  font-weight: bold;
}

.nav-tab.active:hover {
  background-color: #00796b;
}

.nav-tab.disabled {
  background-color: #555;
  cursor: not-allowed;
  pointer-events: none;
  color: #888;
}

.nav-tab.disabled:hover {
  background-color: #555;
}

/* Bouton compte */
.auth-button {
  cursor: pointer;
  padding: 8px 18px;
  color: #00aaff;
  font-weight: bold;
  font-size: 18px;
}

.auth-button:hover {
  text-decoration: underline;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out; 
}

.modal-content {
  background: #ffffff;
  padding: 30px 40px;
  border-radius: 10px;
  width: 350px; 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  animation: scaleIn 0.3s ease-out; 
}

input {
  width: 100%;
  padding: 12px;
  margin: 10px 0; /* Ajouter de l'espacement entre les champs */
  border: 1px solid #ddd; /* Bordure douce */
  border-radius: 8px;
  font-size: 16px;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.cgu-modal {
  max-width: 700px;
  margin: auto;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
}

.cgu-content {
  max-height: 60vh; /* hauteur maximum à 60% de la hauteur de l'écran */
  overflow-y: auto;  /* active le scroll si besoin */
  padding-right: 1rem;
}

input:focus {
  border-color: #009688;
  box-shadow: 0 0 10px rgba(0, 150, 136, 0.3); /* Ombre au focus */
}

/* Boutons */
button {
  width: 100%;
  padding: 12px;
  background-color: #009688; /* Couleur principale */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin: 5px 0;
}

button:hover {
  background-color: #00796b; /* Couleur au survol */
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Titres dans la modale */
h2 {
  text-align: center;
  font-size: 24px;
  color: #333;
  margin-bottom: 20px; /* Espacement sous le titre */
  font-weight: 600;
}

.account-menu {
  position: absolute;
  background-color: white;
  color: #333;
  padding: 10px;
  border-radius: 10px;
  margin-top: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  min-width: 200px;
}

.account-menu > div {
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.account-menu > div:hover {
  background-color: #f0f0f0;
}

.contact {
  font-size: 12px;
  margin-top: 10px;
  color: #888;
  pointer-events: none;
}

</style>
