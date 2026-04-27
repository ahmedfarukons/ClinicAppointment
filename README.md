# 🏥 Klinik Randevu Sistemi (Admin Paneli Destekli)

Bu proje, yapay zeka destekli bir klinik asistanı ve doktor bazlı randevu yönetim sistemidir.

## 🚀 Hızlı Başlangıç

Projeyi kendi bilgisayarınızda çalıştırmak için Docker yüklü olması yeterlidir:

```bash
docker compose up -d --build
```

Uygulama ayağa kalktığında:
- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **Admin Paneli:** `http://localhost:3000/admin/login`

## 🔐 Giriş Bilgileri

### Kullanıcı Tarafı
AI Asistanı ile konuşarak veya doğrudan Randevu Al sayfasından randevu oluşturabilirsiniz.

### Yönetici (Admin) Paneli
Klinik sahibi olarak randevuları yönetmek için:
- **URL:** `http://localhost:3000/admin/login`
- **Kullanıcı Adı:** `admin`
- **Şifre:** `clinic2024`

## ✨ Özellikler
- **AI Triaj:** Şikayete göre uygun tıbbi bölüme yönlendirme.
- **Doktor Seçimi:** Bölüm bazlı doktor listesi ve randevu çakışma kontrolü.
- **Yönetim Paneli:** Randevu onaylama, iptal etme, silme ve CSV dışa aktarma.
- **Responsive Tasarım:** Mobil ve masaüstü uyumlu premium arayüz.

## 🛠️ Teknolojiler
- **Backend:** FastAPI, SQLAlchemy, SQLite, Gemini AI
- **Frontend:** React, React Router, Vanilla CSS
- **Container:** Docker & Docker Compose
