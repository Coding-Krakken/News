# Deployment Guide

## Production Deployment

### Prerequisites

- Node.js 18+ LTS
- PostgreSQL 15+
- Nginx or similar reverse proxy
- SSL/TLS certificate
- Process manager (PM2 recommended)

### Environment Setup

#### 1. Database Setup

```bash
# Create production database
createdb -U postgres news_db

# Create database user
psql -U postgres << EOF
CREATE USER news_user WITH ENCRYPTED PASSWORD 'secure_production_password';
GRANT ALL PRIVILEGES ON DATABASE news_db TO news_user;
EOF

# Run migrations
cd backend
./run-migrations.sh dev
```

#### 2. Backend Configuration

Create `/backend/.env` for production:

```env
NODE_ENV=production
PORT=3000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=your_secure_db_password

# JWT Secrets (generate new ones!)
JWT_ACCESS_SECRET=<64-char-random-hex>
JWT_REFRESH_SECRET=<64-char-random-hex>
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d

# Security
COOKIE_SECRET=<32-char-random-hex>

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
AUTH_RATE_LIMIT_MAX_REQUESTS=5

# CORS
CORS_ORIGIN=https://yourdomain.com

# Logging
LOG_LEVEL=info
```

Generate secrets:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

#### 3. Backend Build & Start

```bash
cd backend
npm ci --production
npm run build

# Install PM2 globally
npm install -g pm2

# Start with PM2
pm2 start dist/index.js --name news-api

# Save PM2 configuration
pm2 save
pm2 startup
```

#### 4. Frontend Configuration

Create `/frontend/.env.production`:

```env
VITE_API_URL=https://api.yourdomain.com/api
```

#### 5. Frontend Build

```bash
cd frontend
npm ci --production
npm run build

# Build output is in dist/ directory
```

### Nginx Configuration

#### Backend Proxy

`/etc/nginx/sites-available/news-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Frontend Serving

`/etc/nginx/sites-available/news-frontend`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://yourdomain.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.yourdomain.com;
    return 301 https://yourdomain.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    root /var/www/news/frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 256;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable sites:
```bash
ln -s /etc/nginx/sites-available/news-api /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/news-frontend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificates
certbot --nginx -d yourdomain.com -d www.yourdomain.com
certbot --nginx -d api.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

### Database Backup

#### Setup automated backups

`/usr/local/bin/backup-news-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/news"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U news_user news_db | gzip > $BACKUP_DIR/news_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "news_db_*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-news-db.sh
```

### Monitoring

#### PM2 Monitoring

```bash
# View logs
pm2 logs news-api

# Monitor processes
pm2 monit

# Status
pm2 status
```

#### Log Rotation

`/etc/logrotate.d/news-api`:

```
/var/log/news-api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
```

### Health Checks

Set up monitoring for:

- API health endpoint: `https://api.yourdomain.com/health`
- Database connection
- Disk space
- Memory usage
- CPU usage

Use tools like:
- Uptime Robot
- Pingdom
- New Relic
- DataDog

### Deployment Script

`deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Backend deployment
echo "Deploying backend..."
cd backend
npm ci --production
npm run build
pm2 restart news-api
cd ..

# Frontend deployment
echo "Deploying frontend..."
cd frontend
npm ci --production
npm run build
rm -rf /var/www/news/frontend/dist
cp -r dist /var/www/news/frontend/
cd ..

echo "Deployment complete!"
```

### Security Checklist

Before going live:

- [ ] Change all default secrets
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall (ufw/iptables)
- [ ] Set up fail2ban for SSH
- [ ] Enable database SSL
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Review and test rate limiting
- [ ] Scan for vulnerabilities
- [ ] Update dependencies
- [ ] Test disaster recovery
- [ ] Document procedures

### Performance Optimization

#### Database

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_bookmarks_user_created 
ON bookmarks(user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_saved_filters_user_created 
ON saved_filters(user_id, created_at DESC);

-- Analyze tables
ANALYZE users;
ANALYZE bookmarks;
ANALYZE saved_filters;
```

#### Node.js

```bash
# Set NODE_ENV
export NODE_ENV=production

# Enable cluster mode with PM2
pm2 start dist/index.js -i max --name news-api
```

### Docker Deployment (Alternative)

#### Dockerfile (Backend)

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

#### docker-compose.yml (Production)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: news_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: news_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      NODE_ENV: production
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: news_db
      DB_USER: news_user
      DB_PASSWORD: ${DB_PASSWORD}
      JWT_ACCESS_SECRET: ${JWT_ACCESS_SECRET}
      JWT_REFRESH_SECRET: ${JWT_REFRESH_SECRET}
      COOKIE_SECRET: ${COOKIE_SECRET}
    depends_on:
      - postgres
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### Rollback Procedure

If deployment fails:

```bash
# Backend rollback
pm2 stop news-api
git checkout <previous-commit>
cd backend
npm ci
npm run build
pm2 start news-api

# Frontend rollback
cd frontend
git checkout <previous-commit>
npm ci
npm run build
cp -r dist /var/www/news/frontend/
```

### Maintenance Mode

Create `maintenance.html` and configure nginx:

```nginx
location / {
    if (-f /var/www/maintenance.html) {
        return 503;
    }
    # ... normal configuration
}

error_page 503 @maintenance;
location @maintenance {
    root /var/www;
    rewrite ^(.*)$ /maintenance.html break;
}
```

Enable/disable:
```bash
# Enable
touch /var/www/maintenance.html

# Disable
rm /var/www/maintenance.html
```
