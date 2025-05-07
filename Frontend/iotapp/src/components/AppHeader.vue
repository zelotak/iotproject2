<template>
  <div>
    <header class="app-header">
      <div class="header-content">
        <h1>IOT Pentesting</h1>
        <p class="subtitle">Analyse et test des protocoles IoT courants</p>
      </div>
      <div class="navbar">
        <ul>
          <li :class="{ active: activeTab === 'SCAN' }" @click="selectTab('SCAN')">SCAN</li>
          <li :class="{ active: activeTab === 'MQTT', disabled: !testsStarted }" @click="selectTab('MQTT')">MQTT</li>
          <li :class="{ active: activeTab === 'COAP', disabled: !testsStarted }" @click="selectTab('COAP')">COAP</li>
          <li :class="{ active: activeTab === 'MODBUS', disabled: !testsStarted }" @click="selectTab('MODBUS')">MODBUS</li>
          <li :class="{ active: activeTab === 'OPCUA', disabled: !testsStarted }" @click="selectTab('OPCUA')">OPCUA</li>
          <li :class="{ active: activeTab === 'AMQP', disabled: !testsStarted }" @click="selectTab('AMQP')">AMQP</li>
          <li class="auth-button" @click="toggleAccountMenu">
            <span v-if="isLoggedIn">{{ username }}</span>
            <span v-else>Compte</span>
            <div v-if="showAccountMenu" class="account-menu">
              <template v-if="!isLoggedIn">
                <div @click="toggleLoginModal">Se connecter</div>
                <div @click="toggleRegisterModal">Créer un compte</div>
              </template>
              <template v-else>
                <div>Status : <strong>{{ isPremium ? 'Premium' : 'Standard' }}</strong></div>
                <div v-if="!isPremium" @click="upgradeToPremium">Passer Premium</div>
                <div @click="logout">Déconnexion</div>
              </template>
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
      loginUsername: '',
      loginPassword: '',
      registerUsername: '',
      registerPassword: '',
      showAccountMenu: false,
      isPremium: false
    };
  },
  mounted() {
    this.checkLoginStatus();
  },
  methods: {
    selectTab(tab) {
      if (this.testsStarted || tab === 'SCAN') {
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
    toggleAccountMenu() {
      this.showAccountMenu = !this.showAccountMenu;
    },
    upgradeToPremium() {
      alert("Redirection vers la page de paiement (à implémenter)");
    },
    async login(username, password) {
      try {
        const { data } = await axios.post('http://127.0.0.1:5000/login', {
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
        await axios.post('http://127.0.0.1:5000/register', { username, password });
        alert("Compte créé avec succès !");
        await this.login(username, password);
        this.closeRegisterModal();
      } catch (err) {
        console.error("Erreur d'inscription", err);
        alert("Erreur lors de l'inscription");
      }
    },
    async logout() {
      try {
        await axios.post('http://127.0.0.1:5000/logout');

        localStorage.removeItem('isConnected');
        localStorage.removeItem('isPremium');
        localStorage.removeItem('username');

        this.isLoggedIn = false;
        this.username = '';
        this.isPremium = false;
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

/* Style de la barre de navigation (les onglets) */
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
  display: flex; /* Aligne les éléments horizontalement */
  gap: 30px; /* Espacement égal entre les onglets */
  padding: 0;
  margin: 0;
}

.navbar li {
  padding: 8px 18px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  border-radius: 25px;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.navbar li:hover {
  background-color: #2a3c52;
  transform: scale(1.1);
}

.navbar li.active {
  background-color: #009688;
  color: white;
  font-weight: bold;
}

.navbar li.active:hover {
  background-color: #00796b;
}

/* Griser les onglets désactivés */
.navbar li.disabled {
  background-color: #555; /* Gris pour les onglets désactivés */
  cursor: not-allowed;
  pointer-events: none; 
  color: #888;
}

.navbar li.disabled:hover {
  background-color: #555; /* Pas de changement au survol pour les onglets désactivés */
}

.auth-button {
  cursor: pointer;
  color: #00aaff;
  font-weight: bold;
  font-size: 16px;
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
