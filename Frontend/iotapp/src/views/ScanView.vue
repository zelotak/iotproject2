<template>
  <div class="scan-view">
    <div class="content-wrapper">
      <header class="header">
        <h2>Pentesting IoT</h2>
        <p>Lancez une analyse réseau pour découvrir les services ouverts sur votre réseau IoT.</p>
      </header>

      <section class="card scan-form">
        <h3>Paramètres du scan</h3>
        <div class="form-group">
          <label for="network">Adresse réseau</label>
          <input
            id="network"
            v-model="localNetwork"
            type="text"
            placeholder="192.168.1.0"
            :disabled="isLoading"
          />
        </div>
        <div class="form-group">
          <label for="mask">Masque de sous-réseau</label>
          <input
            id="mask"
            v-model="localMask"
            type="text"
            placeholder="24"
            :disabled="isLoading"
          />
        </div>
        <button @click="startScan" :disabled="isLoading">
          <span v-if="!isLoading">Démarrer le scan</span>
          <span v-else>Chargement...</span>
        </button>
      </section>

      <section v-if="scanResults.length" class="card scan-results">
        <h3>Résultats du scan</h3>
        <table>
          <thead>
            <tr>
              <th>Hôte</th>
              <th>Port</th>
              <th>Protocole</th>
              <th>État</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in scanResults" :key="i">
              <td>{{ r.host }}</td>
              <td>{{ r.port }}</td>
              <td>{{ r.protocol }}</td>
              <td>{{ r.state }}</td>
            </tr>
          </tbody>
        </table>

        <div class="test-button-wrapper">
          <button @click="startTests" :disabled="!scanResults.length || isLoadingTests">
            <span v-if="!isLoadingTests">Lancer les tests</span>
            <span v-else>Chargement...</span>
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ScanView',
  props: {
    scanResults: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      localNetwork: '',
      localMask: '',
      isLoading: false,
      isLoadingTests: false
    };
  },
  methods: {
    isConnected() {
      return localStorage.getItem('isConnected') === 'true';
    },

    async startScan() {
      if (!this.isConnected()) {
        return alert('Vous devez être connecté pour effectuer cette action.');
      }

      if (!this.localNetwork || !this.localMask) {
        return alert("L'adresse réseau et le masque de sous-réseau sont requis.");
      }

      this.isLoading = true;
      try {
        const { data } = await axios.post('http://localhost:5000/scan', {
          username: localStorage.getItem('username'),
          network: this.localNetwork,
          mask: this.localMask
        });

        if (!Array.isArray(data.results)) {
          throw new Error('Format de réponse inattendu');
        }

        const formatted = data.results.map(r => ({
          host: r.host,
          port: r.port,
          protocol: r.protocol,
          state: r.state
        }));

        this.$emit('update:scanResults', formatted);
      } catch (err) {
        console.error('Erreur lors du scan :', err.response?.data || err.message);
        alert('Erreur lors du scan. Consultez la console pour plus de détails.');
      } finally {
        this.isLoading = false;
      }
    },

    async startTests() {
      if (!this.isConnected()) {
        return alert('Vous devez être connecté pour effectuer cette action.');
      }

      this.isLoadingTests = true;
      try {
        const { data } = await axios.post('http://localhost:5000/pentest', {
          username: localStorage.getItem('username')
        });

        this.$emit('update:testResults', data);
        this.$emit('testsStarted', true);
      } catch (err) {
        console.error('Erreur lors des tests :', err.response?.data || err.message);
        alert('Erreur lors du lancement des tests. Consultez la console pour plus de détails.');
      } finally {
        this.isLoadingTests = false;
      }
    }
  }
};
</script>

<style scoped>
.scan-view {
  display: flex;
  justify-content: center;
  padding-top: 32px; /* espace entre le haut de page et le contenu */
  padding-bottom: 48px;
  background-color: #f9fafb;
  min-height: 100vh;
  box-sizing: border-box;
}

.content-wrapper {
  width: 100%;
  max-width: 800px;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Header */
.header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 8px;
  text-align: center;
}

.header p {
  font-size: 15px;
  color: #6c757d;
  text-align: center;
  margin: 0;
}

/* Card */
.card {
  background-color: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

/* Form title */
.scan-form h3,
.scan-results h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
}

/* Inputs */
.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #fefefe;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #009688;
  outline: none;
}

button {
  background-color: #009688;
  color: white;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
}

button:hover {
  background-color: #00796b;
}

/* Table */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

th, td {
  padding: 14px;
  border: 1px solid #e0e0e0;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  color: #333;
}

tr:nth-child(even) {
  background-color: #fbfbfb;
}

tr:hover {
  background-color: #f1f1f1;
}

.test-button-wrapper {
  margin-top: 20px;
}

</style>
