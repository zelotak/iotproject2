<template>
  <div id="app">
    <AppHeader @changeTab="currentTab = $event" :scanStarted="scanStarted" />
    <div class="content">
      <ScanView
        v-if="currentTab === 'SCAN'"
        :network="network"
        :subnetMask="subnetMask"
        :scanResults="scanResults"
        @update:network="network = $event"
        @update:subnetMask="subnetMask = $event"
        @update:scanResults="scanResults = $event"
        @scanStarted="scanStarted = true"
      />
      <div v-else style="padding: 20px;">Fonctionnalité à venir.</div>
    </div>
  </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import ScanView from './views/ScanView.vue';

export default {
  components: {
    AppHeader,
    ScanView
  },
  data() {
    return {
      currentTab: 'SCAN',
      scanStarted: false,
      network: '',
      subnetMask: '',
      scanResults: []
    };
  }
};
</script>


<style>
/* Style global du layout */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* Prendre toute la hauteur */
}

/* Décale le contenu en dessous de la Sidebar et du Header */
.content {
  flex-grow: 1;
  padding: 20px;
  margin: 20px auto 0 auto; 
  max-width: 1100px;
}
</style>
