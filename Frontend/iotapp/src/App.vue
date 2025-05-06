<template>
  <div id="app">
    <AppHeader 
      @changeTab="currentTab = $event" 
      :scanStarted="scanStarted"
      :testsStarted="testsStarted"
    />
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
        @update:testResults="testResults = $event"
        @testsStarted="testsStarted = true" 
      />
      <TabMqtt v-if="currentTab === 'MQTT'" :testResults="testResults" />
      <TabCoap v-if="currentTab === 'COAP'" :testResults="testResults" />
      <TabModbus v-if="currentTab === 'MODBUS'" :testResults="testResults" />
      <TabOpcua v-if="currentTab === 'OPCUA'" :testResults="testResults" />
      <TabAmqp v-if="currentTab === 'AMQP'" :testResults="testResults" />
    </div>
  </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import ScanView from './views/ScanView.vue';
import TabMqtt from './views/TabMqtt.vue';   
import TabCoap from './views/TabCoap.vue';  
import TabModbus from './views/TabModbus.vue'; 
import TabOpcua from './views/TabOpcua.vue';  
import TabAmqp from './views/TabAmqp.vue';  

export default {
  components: {
    AppHeader,
    ScanView,
    TabAmqp,  
    TabCoap,  
    TabModbus, 
    TabOpcua,  
    TabMqtt    
  },
  data() {
    return {
      currentTab: 'SCAN',
      scanStarted: false,
      testsStarted: false,
      network: '',
      subnetMask: '',
      scanResults: [],
      testResults: []
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
