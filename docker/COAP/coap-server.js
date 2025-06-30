const coap = require('coap');
const url = require('url');

const server = coap.createServer();

let sensorData = null;
const observers = new Set();

// Fonction pour notifier tous les observateurs
function notifyObservers() {
  observers.forEach(res => {
    res.write(JSON.stringify({ data: sensorData, timestamp: Date.now() }));
  });
}

server.on('request', (req, res) => {
  const reqUrl = url.parse(req.url).pathname;
  console.log("Requête reçue:", reqUrl); // Log supplémentaire pour voir la route demandée
  
  // Vérification de la route invalide
  if (reqUrl !== '/sensor-data') {
    console.log('Route invalide détectée:', reqUrl); // Log pour indiquer la route invalide
    res.code = '4.04';  // Renvoie 404
    return res.end('Not Found');  // Arrête le traitement ici
  }

  // Handle PUT
  if (req.method === 'PUT') {
    try {
      const payload = JSON.parse(req.payload.toString());
      console.log('Payload reçu (PUT):', payload);

      if (!payload || typeof payload !== 'object' || !payload.value) {
        res.code = '4.00';
        return res.end('Bad Request: payload mal formé');
      }

      sensorData = payload;
      res.code = '2.04';
      res.end('Updated');
      notifyObservers(); // Notify clients in observe mode

    } catch (e) {
      res.code = '4.00';
      return res.end('Bad Request: payload JSON invalide');
    }
  }

  // Handle GET with Observe
  else if (req.method === 'GET') {
    if (req.headers['Observe'] === 0) {
      // Client veut observer
      res.setOption('Content-Format', 'application/json');
      res.code = '2.05';
      res.write(JSON.stringify({ data: sensorData, timestamp: Date.now() }));
      observers.add(res);
      console.log('Nouveau client en observation');

      // Enlever l'observateur si la connexion se ferme
      res.on('finish', () => {
        observers.delete(res);
        console.log('Le client a quitte l observation');
      });
    } else {
      // GET normal (pas observe)
      res.setOption('Content-Format', 'application/json');
      console.log('Requête GET normale');
      res.code = '2.05';
      res.end(JSON.stringify({ data: sensorData, timestamp: Date.now() }));
    }
  }

  // Méthode non supportée
  else {
    res.code = '4.05';
    res.end('Method Not Allowed');
  }
});

server.listen(() => {
  console.log('🌍 Serveur COAP lancé sur port 5683');
});
