# Utiliser Node.js LTS
FROM node:18-alpine

# Créer un répertoire de travail
WORKDIR /app

# Installer les dépendances FIRST pour optimiser le cache
COPY package*.json ./
RUN npm install --production

# Copier le code applicatif
COPY coap-server.js .

# Sécurité : Utilisateur non-root
RUN chown -R node:node /app
USER node

# Configuration réseau
EXPOSE 5683/udp

# Point d'entrée
CMD ["node", "coap-server.js"]
