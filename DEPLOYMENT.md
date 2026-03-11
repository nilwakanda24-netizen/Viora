# 🚀 Guia de Desplegament de Viora

## Opcions per fer Viora permanent i accessible

### Opció 1: Desplegament Gratuït amb Render.com (RECOMANAT)

**Avantatges:**
- ✅ Gratuït
- ✅ HTTPS automàtic
- ✅ URL pública permanent
- ✅ Fàcil de configurar

**Passos:**

1. **Crear compte a Render.com**
   - Ves a https://render.com
   - Registra't amb GitHub/GitLab/Email

2. **Preparar el projecte**
   ```bash
   # Ja està tot preparat! Només necessites pujar-ho a GitHub
   ```

3. **Crear repositori GitHub**
   - Ves a https://github.com/new
   - Crea un repositori nou (públic o privat)
   - Puja el codi:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Viora Medical AI"
   git branch -M main
   git remote add origin https://github.com/EL-TEU-USUARI/viora.git
   git push -u origin main
   ```

4. **Desplegar a Render**
   - A Render.com, clica "New +" → "Web Service"
   - Connecta el teu repositori GitHub
   - Configuració:
     - **Name:** viora-medical-ai
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python viora_ultimate.py`
     - **Plan:** Free
   - Clica "Create Web Service"

5. **Configurar variables d'entorn (opcional)**
   - A la configuració del servei, afegeix:
     - `PYTHON_VERSION`: 3.11.0

**URL final:** `https://viora-medical-ai.onrender.com`

---

### Opció 2: Desplegament amb Railway.app

**Avantatges:**
- ✅ Molt fàcil
- ✅ $5 crèdit gratuït mensual
- ✅ Desplegament automàtic

**Passos:**

1. Ves a https://railway.app
2. Connecta GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecciona el teu repositori
5. Railway detecta automàticament Python i desplega

**URL final:** `https://viora-production.up.railway.app`

---

### Opció 3: Desplegament amb Vercel (Serverless)

**Nota:** Requereix adaptació per funcions serverless

1. Instal·la Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Desplega:
   ```bash
   vercel
   ```

---

### Opció 4: Servidor Propi (VPS)

**Per a producció professional amb control total**

#### 4.1. Contractar VPS

Opcions recomanades:
- **DigitalOcean** (5$/mes): https://www.digitalocean.com
- **Linode** (5$/mes): https://www.linode.com
- **Hetzner** (4€/mes): https://www.hetzner.com
- **AWS EC2** (gratuït 1 any): https://aws.amazon.com/free

#### 4.2. Configurar servidor Ubuntu

```bash
# Connectar per SSH
ssh root@LA-TEVA-IP

# Actualitzar sistema
apt update && apt upgrade -y

# Instal·lar Python i dependències
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Instal·lar Tesseract per OCR
apt install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-cat

# Crear usuari
adduser viora
usermod -aG sudo viora
su - viora

# Clonar projecte
git clone https://github.com/EL-TEU-USUARI/viora.git
cd viora

# Crear entorn virtual
python3 -m venv venv
source venv/bin/activate

# Instal·lar dependències
pip install -r requirements.txt
```

#### 4.3. Configurar com a servei systemd

```bash
sudo nano /etc/systemd/system/viora.service
```

Contingut:
```ini
[Unit]
Description=Viora Medical AI Platform
After=network.target

[Service]
User=viora
WorkingDirectory=/home/viora/viora
Environment="PATH=/home/viora/viora/venv/bin"
ExecStart=/home/viora/viora/venv/bin/python viora_ultimate.py

[Install]
WantedBy=multi-user.target
```

Activar servei:
```bash
sudo systemctl daemon-reload
sudo systemctl enable viora
sudo systemctl start viora
sudo systemctl status viora
```

#### 4.4. Configurar Nginx com a reverse proxy

```bash
sudo nano /etc/nginx/sites-available/viora
```

Contingut:
```nginx
server {
    listen 80;
    server_name viora.elteudomini.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Per a càrrega de fitxers grans
        client_max_body_size 50M;
    }
}
```

Activar:
```bash
sudo ln -s /etc/nginx/sites-available/viora /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4.5. Configurar HTTPS amb Let's Encrypt

```bash
sudo certbot --nginx -d viora.elteudomini.com
```

---

### Opció 5: Docker (Portabilitat màxima)

Crea `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Instal·lar Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-cat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "viora_ultimate.py"]
```

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  viora:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./viora_comments.db:/app/viora_comments.db
    restart: unless-stopped
```

Executar:
```bash
docker-compose up -d
```

---

## Configuració de Domini

### Comprar domini

Opcions recomanades:
- **Namecheap**: https://www.namecheap.com (~10€/any)
- **Google Domains**: https://domains.google
- **Cloudflare**: https://www.cloudflare.com/products/registrar/

### Configurar DNS

Afegeix un registre A apuntant a la IP del teu servidor:

```
Type: A
Name: viora (o @)
Value: LA-TEVA-IP-DEL-SERVIDOR
TTL: 3600
```

---

## Millores per Producció

### 1. Base de dades PostgreSQL

Substitueix SQLite per PostgreSQL per millor rendiment:

```bash
pip install psycopg2-binary
```

### 2. Redis per caché

```bash
pip install redis
```

### 3. Monitorització

Afegeix Sentry per tracking d'errors:

```bash
pip install sentry-sdk
```

### 4. Backup automàtic

Crea script de backup:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/viora_$DATE.tar.gz /home/viora/viora
```

Afegeix a crontab:
```bash
0 2 * * * /home/viora/backup.sh
```

---

## Costos Estimats

| Opció | Cost Mensual | Dificultat |
|-------|--------------|------------|
| Render.com (Free) | 0€ | ⭐ Fàcil |
| Railway.app | 0-5€ | ⭐ Fàcil |
| DigitalOcean VPS | 5€ | ⭐⭐ Mitjà |
| AWS EC2 | 0€ (1r any) | ⭐⭐⭐ Difícil |
| Domini | 10€/any | ⭐ Fàcil |

---

## Recomanació Final

**Per començar:** Render.com (gratuït, fàcil)
**Per producció:** VPS amb Nginx + HTTPS (control total)
**Per escalar:** AWS/Google Cloud amb Kubernetes

---

## Suport i Manteniment

### Actualitzar l'aplicació

```bash
cd /home/viora/viora
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart viora
```

### Veure logs

```bash
sudo journalctl -u viora -f
```

### Monitoritzar recursos

```bash
htop
```

---

## Seguretat

### Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Actualitzacions automàtiques

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Contacte i Ajuda

Si necessites ajuda amb el desplegament:
- GitHub Issues
- Email: suport@viora.com
- Documentació: https://docs.viora.com

---

**Fet amb ❤️ per la comunitat mèdica**
