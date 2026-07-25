FROM node:22-alpine

WORKDIR /app

# Install dependencies first (layer-cached separately from source)
COPY package*.json ./
RUN npm ci --omit=dev

# Copy application source
COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
