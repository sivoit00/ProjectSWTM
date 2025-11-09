FROM node:20-slim

WORKDIR /app

# Dependencies installieren
COPY package*.json ./
RUN npm ci --silent
# Ensure optional SWC React plugin is available (fixes missing @vitejs/plugin-react-swc error)
RUN npm install --no-audit --silent --save-dev @vitejs/plugin-react-swc

# Code kopieren
COPY . .

# Wichtig: Als root laufen lassen (für Development)
# In Production würde man non-root nutzen

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]