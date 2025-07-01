<template>
    <div class="tab-amqp">
      <!-- Score global -->
      <div class="header">
        <h1>Résultats de l’audit AMQP</h1>
        <div class="score-box">
          <span>Score global :</span>
          <strong class="score-value">{{ score }} / 100</strong>
          <div class="score-bar">
            <div class="score-fill" :style="{ width: score + '%' }"></div>
          </div>
        </div>
      </div>
  
      <!-- Message contact pour utilisateurs premium -->
      <div v-if="isPremium" class="premium-contact">
        <p><strong>En tant qu'utilisateur Premium,</strong> vous pouvez contacter notre équipe pour une mise à niveau sécurisée de votre infrastructure :</p>
        <p>📞 <a href="mailto:support@pentestiot.io">support@pentestiot.io</a> (lun–ven, 9h–18h)</p>
      </div>
  
      <!-- Liste des tests -->
      <div class="test-grid">
        <div
          v-for="(test, index) in amqpTests"
          :key="index"
          class="test-card"
          :class="{ vuln: test.vulne, safe: !test.vulne }"
        >
          <h2>{{ test.test }}</h2>
          <div class="status">
            <span class="emoji">{{ test.vulne ? '❌' : '✅' }}</span>
            <span class="label">{{ test.vulne ? 'Vulnérable' : 'Sécurisé' }}</span>
          </div>

          <!-- Détail du test pour Premium -->
          <p v-if="isPremium" class="detail">{{ test.detail }}</p>
          <p v-else class="detail-disabled"><em>Abonnez-vous pour voir les détails</em></p>
  
          <!-- Explications pour Premium -->
          <div v-if="isPremium && explanations[test.test]" class="explanation">
            <p><strong>📘 Explication :</strong> {{ explanations[test.test].explanation }}</p>
            <p><strong>🛡️ Attaque empêchée :</strong> {{ explanations[test.test].attack_prevented }}</p>
            <p><strong>✅ Bonne pratique :</strong> {{ explanations[test.test].best_practice }}</p>
          </div>
  
          <!-- Message absence d'explication -->
          <div v-else class="no-expl">
            <em v-if="!isPremium">Les explications sont réservées aux utilisateurs premium.</em>
            <em v-else>Pas d’explication disponible pour ce test.</em>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import explanationsJSON from '@/assets/test_explanations.json'
  
  export default {
    name: 'TabAmqp',
    props: {
      testResults: {
        type: Object,
        required: true
      },
      isPremium: {
        type: Boolean,
        required: true
      }
    },
    computed: {
      amqpTests() {
        return (this.testResults.amqp || []).filter(t => 'test' in t)
      },
      score() {
        const scoreEntry = (this.testResults.amqp || []).find(t => 'score' in t)
        return scoreEntry ? scoreEntry.score : 0
      },
      explanations() {
        const amqpExplanations = explanationsJSON['AMQP'] || []
        return Object.fromEntries(amqpExplanations.map(e => [e.test, e]))
      }
    }
  }
  </script>
  
  <style scoped>
  .tab-amqp {
    padding: 1rem;
    font-family: Arial, sans-serif;
  }
  
  .header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  
  .score-box {
    max-width: 300px;
  }
  .score-value {
    font-size: 1.2rem;
    color: #2563eb;
  }
  .score-bar {
    background: #e5e7eb;
    height: 10px;
    border-radius: 5px;
    margin-top: 5px;
  }
  .score-fill {
    background-color: #10b981;
    height: 100%;
    border-radius: 5px;
    transition: width 0.4s ease;
  }
  
  .premium-contact {
    background: #f0f9ff;
    border-left: 4px solid #3b82f6;
    padding: 1rem;
    margin-bottom: 1.5rem;
    border-radius: 4px;
    color: #1e3a8a;
  }
  .premium-contact a {
    color: #1e40af;
    text-decoration: underline;
  }
  
  /* Grid layout: plusieurs cartes par ligne */
  .test-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  
  .test-card {
    background: #fff;
    border-left: 6px solid;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }
  .test-card.vuln {
    border-color: #ef4444;
  }
  .test-card.safe {
    border-color: #10b981;
  }
  
  h2 {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }
  
  .status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  .status .emoji {
    font-size: 1.3rem;
  }
  .status .label {
    font-weight: bold;
    color: #374151;
  }
  
  .detail, .detail-disabled {
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
  }
  .detail-disabled {
    font-style: italic;
    color: #9ca3af;
  }
  
  .explanation {
    font-size: 0.9rem;
    background: #f3f4f6;
    padding: 0.75rem;
    border-radius: 6px;
  }
  .no-expl {
    font-size: 0.85rem;
    font-style: italic;
    color: #9ca3af;
  }
  
  </style>
