<template>
  <header class="app-header">
    <!-- Contenu du header avec titre et sous-titre -->
    <div class="header-content">
      <h1>IOT Pentesting</h1>
      <p class="subtitle">Analyse et test des protocoles IoT courants</p>
    </div>
    <!-- Barre de navigation (les onglets) sous le titre -->
    <div class="navbar">
      <ul>
        <li :class="{ active: activeTab === 'SCAN' }" @click="selectTab('SCAN')">SCAN</li>
        <li :class="{ active: activeTab === 'MQTT', disabled: !scanStarted }" @click="selectTab('MQTT')">MQTT</li>
        <li :class="{ active: activeTab === 'COAP', disabled: !scanStarted }" @click="selectTab('COAP')">COAP</li>
        <li :class="{ active: activeTab === 'MODBUS', disabled: !scanStarted }" @click="selectTab('MODBUS')">MODBUS</li>
        <li :class="{ active: activeTab === 'OPCUA', disabled: !scanStarted }" @click="selectTab('OPCUA')">OPCUA</li>
        <li :class="{ active: activeTab === 'AMQP', disabled: !scanStarted }" @click="selectTab('AMQP')">AMQP</li>
      </ul>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    scanStarted: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'SCAN'
    };
  },
  methods: {
    selectTab(tab) {
      // On permet le clic sur SCAN ou si le scan a démarré
      if (this.scanStarted || tab === 'SCAN') {
        this.activeTab = tab;
        this.$emit('changeTab', tab);
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
  padding: 12px 25px;
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
</style>
