FROM node:20-slim

WORKDIR /app

# Install system deps (falls nötig), dann Abhängigkeiten installieren
COPY package*.json ./
RUN npm ci --silent

# Kopiere Rest und setze Berechtigungen für non-root user
COPY . .

# Optional: lege einen non-root user an und übernehme Besitz (verbessert Sicherheit und verhindert EACCES)
RUN groupadd -r app && useradd -r -g app app \
    && chown -R app:app /app

USER app

ENV HOST=0.0.0.0
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]