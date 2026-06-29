FROM node:18-alpine

# Variables d'environnement
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Installation des dépendances système
RUN apk add --no-cache libc6-compat

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances (toutes, car en dev on a besoin des devDeps + plugins Tailwind)
RUN npm install

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 3000

# Commande par défaut
CMD ["npm", "run", "dev"]
