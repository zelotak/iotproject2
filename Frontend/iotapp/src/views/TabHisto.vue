<template>
  <div class="scan-view">
    <div class="content-wrapper">

      <!-- Accès Premium -->
      <div v-if="isPremium">
        <header class="header">
          <h2>Historique des scans</h2>
          <p>Consultez ou comparez vos audits précédents en choisissant une période.</p>
        </header>

        <div class="card history-content">
          <!-- Mode Comparaison -->
          <div class="compare-toggle" style="margin-bottom: 24px;">
            <label>
              <input type="checkbox" v-model="enableCompare" />
              Activer la comparaison entre deux audits
            </label>
          </div>

          <!-- Filtres et sélections -->
          <div class="compare-grid">
            <!-- Colonne de gauche -->
            <div class="compare-col">
              <div class="filter-bar">
                <div class="form-field">
                  <label for="start1">Date de début</label>
                  <input type="date" id="start1" v-model="startDateA" />
                </div>
                <div class="form-field">
                  <label for="end1">Date de fin</label>
                  <input type="date" id="end1" v-model="endDateA" />
                </div>
                <button class="submit-btn" @click="fetchScanList('A')">Afficher</button>
              </div>
              <div v-if="scanHistoryA.length" class="dropdown-result">
                <label>Sélectionnez un audit</label>
                <select v-model="selectedScanA">
                  <option disabled value="">-- Choisir --</option>
                  <option v-for="scan in scanHistoryA" :key="scan.id" :value="scan.id">
                    {{ formatScanLabel(scan) }}
                  </option>
                </select>
              </div>
              <p v-if="!scanHistoryA.length" class="empty-msg">Aucun résultat dans la période.</p>

              <div v-if="detailsA" class="card scan-details">
                <h3 class="details-title">{{ scanTitle(selectedScanA, scanHistoryA) }}</h3>
                <p class="details-score">Score : <strong>{{ detailsA.score }}</strong></p>
                <ul class="test-list">
                  <li v-for="(t, i) in detailsA.tests" :key="i" class="test-entry">
                    <span class="test-name">{{ t.test }}</span>
                    <span class="test-status" :class="{ vulnerable: t.vulne }">
                      {{ t.vulne ? "🔴 Vulnérable" : "🟢 Protégé" }}
                    </span>
                    <p class="test-detail">{{ t.detail }}</p>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Colonne de droite si comparaison activée -->
            <div class="compare-col" v-if="enableCompare">
              <div class="filter-bar">
                <div class="form-field">
                  <label for="start2">Date de début</label>
                  <input type="date" id="start2" v-model="startDateB" />
                </div>
                <div class="form-field">
                  <label for="end2">Date de fin</label>
                  <input type="date" id="end2" v-model="endDateB" />
                </div>
                <button class="submit-btn" @click="fetchScanList('B')">Afficher</button>
              </div>
              <div v-if="scanHistoryB.length" class="dropdown-result">
                <label>Sélectionnez un audit</label>
                <select v-model="selectedScanB">
                  <option disabled value="">-- Choisir --</option>
                  <option v-for="scan in scanHistoryB" :key="scan.id" :value="scan.id" :disabled="scan.id === selectedScanA">
                    {{ formatScanLabel(scan) }}
                  </option>
                </select>
              </div>
              <p v-if="!scanHistoryB.length" class="empty-msg">Aucun résultat dans la période.</p>

              <div v-if="detailsB" class="card scan-details">
                <h3 class="details-title">{{ scanTitle(selectedScanB, scanHistoryB) }}</h3>
                <p class="details-score">Score : <strong>{{ detailsB.score }}</strong></p>
                <ul class="test-list">
                  <li v-for="(t, i) in detailsB.tests" :key="i" class="test-entry">
                    <span class="test-name">{{ t.test }}</span>
                    <span class="test-status" :class="{ vulnerable: t.vulne }">
                      {{ t.vulne ? "🔴 Vulnérable" : "🟢 Protégé" }}
                    </span>
                    <p class="test-detail">{{ t.detail }}</p>
                  </li>
                </ul>
              </div>
            </div>
          </div> <!-- /compare-grid -->
        </div>
      </div>

      <!-- Non-premium -->
      <div v-else class="premium-locked card">
        <h2>Accès réservé aux membres Premium</h2>
        <p>Vous devez activer un abonnement Premium pour accéder à ces fonctionnalités.</p>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TabHisto',
  props: {
    username: String,
    isPremium: Boolean
  },
  data() {
    return {
      startDateA: '',
      endDateA: '',
      startDateB: '',
      endDateB: '',
      scanHistoryA: [],
      scanHistoryB: [],
      selectedScanA: '',
      selectedScanB: '',
      detailsA: null,
      detailsB: null,
      enableCompare: false
    };
  },
  watch: {
    selectedScanA(val) {
      this.detailsA = null;
      if (val) this.fetchScanDetails(val, 'A');
    },
    selectedScanB(val) {
      this.detailsB = null;
      if (val) this.fetchScanDetails(val, 'B');
    }
  },
  methods: {
    async fetchScanList(target) {
      const start = this[`startDate${target}`];
      const end = this[`endDate${target}`];
      if (!this.username || !start || !end) return;

      try {
        const { data } = await axios.post('http://localhost:5000/history/list', {
          username: this.username,
          startDate: start,
          endDate: end
        });
        this[`scanHistory${target}`] = data.scans;
        this[`selectedScan${target}`] = '';
        this[`details${target}`] = null;
      } catch (err) {
        console.error(`Erreur chargement scans ${target} :`, err);
        alert(`Erreur lors du chargement des scans (${target})`);
      }
    },

    async fetchScanDetails(id, target) {
      try {
        const { data } = await axios.post('http://localhost:5000/history/details', { id });
        this[`details${target}`] = data;
      } catch (err) {
        console.error(`Erreur chargement détails (${target}) :`, err);
      }
    },

    formatScanLabel(scan) {
      return `${scan.created_at} – ${scan.protocol} sur ${scan.target}`;
    },

    scanTitle(selectedId, list) {
      const found = list.find(s => s.id === selectedId);
      return found ? `${found.protocol} | ${found.target} | ${found.created_at}` : '';
    }
  }
};
</script>

<style scoped>
.compare-grid {
  display: flex;
  flex-direction: row;
  gap: 24px;
  flex-wrap: wrap;
}

.compare-col {
  flex: 1;
  min-width: 300px;
}

.scan-view {
  display: flex;
  justify-content: center;
  padding-top: 32px;
  padding-bottom: 48px;
  background-color: #f9fafb;
  min-height: 100vh;
  box-sizing: border-box;
}

.content-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  box-sizing: border-box;
}

/* Carte blanche */
.card {
  background-color: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

/* Accès premium bloqué */
.premium-locked h2 {
  font-size: 24px;
  margin-bottom: 12px;
  color: #c0392b;
}
.premium-locked p {
  color: #555;
  line-height: 1.5;
}

/* En-tête */
.header {
  text-align: center;
  margin-bottom: 24px;
}
.header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 8px;
}
.header p {
  font-size: 15px;
  color: #6c757d;
  margin: 0;
}

/* Zone filtres */
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}
.form-field {
  display: flex;
  flex-direction: column;
}
.form-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

/* Inputs & select */
.form-field input[type="date"],
.dropdown-result select {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #fefefe;
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.form-field input[type="date"]:focus,
.dropdown-result select:focus {
  border-color: #009688;
  outline: none;
  background-color: #fff;
}

/* Dropdown bloc */
.dropdown-result {
  margin-bottom: 20px;
}
.dropdown-result label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

/* Bouton */
.submit-btn {
  width: 100%;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: bold;
  background-color: #009688;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.submit-btn:hover {
  background-color: #00796b;
}

/* Message vide */
.empty-msg {
  text-align: center;
  color: #888;
  font-style: italic;
}

.scan-details {
  border-left: 5px solid #009688;
  animation: fade-in 0.5s ease;
}

.details-title {
  font-size: 22px;
  margin-bottom: 12px;
  color: #34495e;
}

.details-score {
  margin-bottom: 20px;
  font-size: 16px;
  color: #555;
}

.test-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-entry {
  background-color: #f5f9f9;
  padding: 12px 16px;
  border-radius: 8px;
}

.test-name {
  font-weight: bold;
  color: #2c3e50;
}

.test-status {
  float: right;
  font-weight: bold;
}

.test-status.vulnerable {
  color: #e74c3c;
}

.test-detail {
  font-size: 14px;
  color: #555;
  margin-top: 6px;
}

/* Animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

</style>
