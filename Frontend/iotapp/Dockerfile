# Étape 1 : build de l'app Vue
FROM node:20-alpine AS builder

WORKDIR /app
COPY . .

# Installe les dépendances et compile l'app
RUN npm install && npm run build

# Étape 2 : serve statique avec Nginx
FROM nginx:alpine

# Copie les fichiers compilés dans le dossier public de nginx
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

