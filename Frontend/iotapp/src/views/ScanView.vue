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
              :value="network"
              @input="$emit('update:network', $event.target.value)"
              type="text"
              placeholder="192.168.1.0"
            />
          </div>
          <div class="form-group">
            <label for="mask">Masque de sous-réseau</label>
            <input
              id="mask"
              :value="subnetMask"
              @input="$emit('update:subnetMask', $event.target.value)"
              type="text"
              placeholder="255.255.255.0"
            />
          </div>
          <button @click="startScan">Démarrer le scan</button>
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
              <tr v-for="(result, index) in scanResults" :key="index">
                <td>{{ result.host }}</td>
                <td>{{ result.port }}</td>
                <td>{{ result.protocol }}</td>
                <td>{{ result.state }}</td>
              </tr>
            </tbody>
          </table>
  
          <div class="test-button-wrapper">
            <button @click="startTests" :disabled="!scanResults.length">Lancer les tests</button>
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
      network: String,
      subnetMask: String,
      scanResults: Array
    },
    data() {
        return {
            testResults: [] 
        };
    },
    methods: {
      async startScan() {
        try {
          const response = await axios.post('http://localhost:5000/scan', {
            network: this.network,
            mask: this.subnetMask
          });
  
          if (response.data && Array.isArray(response.data.results)) {
            const results = response.data.results.map(result => ({
              host: result.host,
              port: result.port,
              protocol: result.protocol,
              state: result.state
            }));
  
            this.$emit('update:scanResults', results);
          } else {
            this.$emit('update:scanResults', []);
          }
        } catch (error) {
          console.error('Erreur lors du scan:', error);
          alert('Erreur lors du scan. Voir console pour les détails.');
        }
      },
      async startTests() {
        try {
          const response = await axios.post('http://localhost:5000/pentest');
          const results = response.data;

          this.testResults = results;
  
          this.$emit('update:testResults', results);
          this.$emit('testsStarted'); // C'est le bouton "Lancer les tests" qui déverrouille les onglets
        } catch (error) {
          console.error('Erreur lors des tests:', error);
          alert('Erreur lors du lancement des tests. Voir console pour les détails.');
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
