FROM node:18-alpine

WORKDIR /app

# Paket dosyalarını kopyala
COPY package.json package-lock.json* ./

# Bağımlılıkları yükle
RUN npm install

# Proje kodlarını kopyala
COPY . .

# React uygulamasının çalışacağı port
EXPOSE 3000

# Geliştirme sunucusunu başlat
CMD ["npm", "start"]
