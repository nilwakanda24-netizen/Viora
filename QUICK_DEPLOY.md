# 🚀 Desplegament Ràpid de Viora

## Opció més fàcil: Render.com (5 minuts)

### Pas 1: Preparar el codi

```bash
# Crear repositori GitHub
git init
git add .
git commit -m "Viora Medical AI Platform"
```

### Pas 2: Pujar a GitHub

1. Crea un repositori nou a https://github.com/new
2. Puja el codi:

```bash
git remote add origin https://github.com/EL-TEU-USUARI/viora.git
git branch -M main
git push -u origin main
```

### Pas 3: Desplegar a Render

1. Ves a https://render.com i registra't
2. Clica **"New +"** → **"Web Service"**
3. Connecta el teu repositori GitHub
4. Configuració:
   - **Name:** `viora-medical-ai`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python viora_ultimate.py`
   - **Instance Type:** `Free`
5. Clica **"Create Web Service"**

**Fet! La teva web estarà disponible a:**
`https://viora-medical-ai.onrender.com`

---

## Opció Docker (local o servidor)

### Executar amb Docker

```bash
# Construir i executar
docker-compose up -d

# Veure logs
docker-compose logs -f

# Aturar
docker-compose down
```

Accedeix a: http://localhost:8000

---

## Opció VPS (servidor propi)

### 1. Connectar al servidor

```bash
ssh root@LA-TEVA-IP
```

### 2. Instal·lar dependències

```bash
# Actualitzar sistema
apt update && apt upgrade -y

# Instal·lar Python i eines
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Instal·lar Tesseract OCR
apt install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-cat
```

### 3. Clonar i configurar

```bash
# Crear usuari
adduser viora
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

### 4. Crear servei systemd

```bash
sudo nano /etc/systemd/system/viora.service
```

Enganxa:

```ini
[Unit]
Description=Viora Medical AI
After=network.target

[Service]
User=viora
WorkingDirectory=/home/viora/viora
Environment="PATH=/home/viora/viora/venv/bin"
ExecStart=/home/viora/viora/venv/bin/python viora_ultimate.py

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable viora
sudo systemctl start viora
```

### 5. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/viora
```

Enganxa:

```nginx
server {
    listen 80;
    server_name viora.elteudomini.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
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

### 6. Configurar HTTPS

```bash
sudo certbot --nginx -d viora.elteudomini.com
```

**Fet! La teva web estarà a:**
`https://viora.elteudomini.com`

---

## Comparació d'opcions

| Mètode | Temps | Cost | Dificultat | HTTPS |
|--------|-------|------|------------|-------|
| Render.com | 5 min | Gratuït | ⭐ | ✅ |
| Railway | 5 min | 5€/mes | ⭐ | ✅ |
| Docker local | 2 min | Gratuït | ⭐⭐ | ❌ |
| VPS | 30 min | 5€/mes | ⭐⭐⭐ | ✅ |

---

## Recomanació

**Començar:** Render.com (gratuït i fàcil)
**Producció:** VPS amb domini propi

---

## Ajuda

Si tens problemes:
1. Revisa els logs: `docker-compose logs` o `sudo journalctl -u viora -f`
2. Comprova el firewall: `sudo ufw status`
3. Verifica el port: `netstat -tulpn | grep 8000`

---

**Fet! Ara Viora és accessible des d'Internet 🌍**
