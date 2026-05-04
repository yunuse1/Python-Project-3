# Environment Variables Konfigürasyonu

Bu proje artık sensitive veriler için environment variables kullanıyor. Bu sayede API tokenları, secret keyler ve veritabanı bilgileri GitHub'a yüklenmez.

## 📁 Oluşturulan/Güncellenen Dosyalar

### 1. Backend Environment Files
- **`.env`** — Geliştirme ortamı için gerçek konfigürasyon (GIT'e yüklenmez ✓)
- **`.env.example`** — Template dosya, GIT'e yüklenir (örnek değerler içerir)

### 2. Frontend Environment Files
- **`frontend/.env.local`** — Geliştirme ortamı için gerçek konfigürasyon (GIT'e yüklenmez ✓)
- **`frontend/.env.example`** — Template dosya, GIT'e yüklenir (örnek değerler içerir)

### 3. Güncellenen Dosyalar
- **`requirements.txt`** — `python-dotenv` kütüphanesi eklendi
- **`src/app.py`** — Environment variables'ı yükleme eklendi
- **`.gitignore`** — `.env` dosyaları zaten ignore ediliyor ✓
- **`frontend/.gitignore`** — `.env`, `.env.local` eklendi

## 🔐 Backend Configuration (`.env`)

```env
# Security - JWT Configuration
JWT_SECRET_KEY=super-secret-crypto-key-2026-swe210
JWT_ACCESS_TOKEN_EXPIRES_HOURS=2

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/

# API Configuration
API_HOST=127.0.0.1
API_PORT=5000

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_DAY=500
RATE_LIMIT_PER_HOUR=100
```

## 🎨 Frontend Configuration (`frontend/.env.local`)

```env
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Crypto Trading Platform
VITE_APP_VERSION=1.0.0
```

Frontend zaten `config.js`'de `import.meta.env.VITE_API_URL` kullanıyordu, şimdi `.env.local` ile yönetiliyor.

## ✅ Yapılan İşlemler

1. ✓ Backend config'i environment variables'dan yükleniyor
2. ✓ Frontend config'i `.env.local` ile yönetiliyor
3. ✓ `.env` dosyaları `.gitignore`'da (hassas veriler GIT'e gitmez)
4. ✓ `.env.example` dosyaları GIT'e gidiyor (diğer geliştiriciler için template)
5. ✓ `python-dotenv` requirements.txt'e eklendi

## 🚀 Kullanım

### Backend'i çalıştırırken:
- `.env` dosyasının proje kökünde olduğundan emin olun
- `python-dotenv` yüklü olduğundan emin olun: `pip install python-dotenv`

### Frontend'i çalıştırırken:
- `frontend/.env.local` dosyasının mevcut olduğundan emin olun
- Vite otomatik olarak `.env.local` yükleyecek

## 📝 Üretim Ortamı için

Üretim'de `.env` dosyasını oluşturken:
1. `.env.example`'ı kopyalayın
2. Gerçek değerlerle güncelleyin (güçlü JWT secret, production database URI, vs.)
3. Bu dosyayı sunucuya koyun, GitHub'a PUSHlamayın

## 🔒 Güvenlik Uyarısı

⚠️ **Asla** `.env` dosyasını GitHub'a yüklemeyiniz!
⚠️ **Üretim ortamında** güçlü bir `JWT_SECRET_KEY` kullanın
⚠️ **CORS_ORIGINS** üretim'de uygun domain'lere ayarlayın
