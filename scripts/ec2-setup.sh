#!/usr/bin/env bash
# SteadyVox EC2 Instance Setup Script
# Run on a fresh Ubuntu 22.04/24.04 EC2 instance
# Usage: sudo bash scripts/ec2-setup.sh
#
# Prerequisites:
#   - EC2 Security Group allows inbound on ports 22, 80, 443, 9090, 3000
#   - Instance type: t3.medium or larger recommended
#
# DISCLAIMER: Research screening tool only — not a medical diagnosis.

set -euo pipefail

echo "═══════════════════════════════════════════════════════════"
echo "  SteadyVox – EC2 Instance Setup"
echo "  Research screening tool only — not a medical diagnosis."
echo "═══════════════════════════════════════════════════════════"

# ── System Update ─────────────────────────────────────────
echo ""
echo "[1/6] Updating system packages..."
apt-get update && apt-get upgrade -y

# ── Install Docker ────────────────────────────────────────
echo ""
echo "[2/6] Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker ubuntu
    echo "  ✓ Docker installed"
else
    echo "  ✓ Docker already installed ($(docker --version))"
fi

# ── Install Docker Compose Plugin ─────────────────────────
echo ""
echo "[3/6] Installing Docker Compose plugin..."
apt-get install -y docker-compose-plugin
systemctl enable docker
systemctl start docker
echo "  ✓ Docker Compose ready ($(docker compose version))"

# ── Setup Application Directory ───────────────────────────
echo ""
echo "[4/6] Setting up application directory..."
mkdir -p /opt/steadyvox
chown ubuntu:ubuntu /opt/steadyvox

if [ ! -d /opt/steadyvox/.git ]; then
    git clone https://github.com/saravana/SteadyVox.git /opt/steadyvox
    echo "  ✓ Repository cloned"
else
    cd /opt/steadyvox && git pull origin main
    echo "  ✓ Repository updated"
fi

cd /opt/steadyvox

# ── Environment Configuration ─────────────────────────────
echo ""
echo "[5/6] Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠ Created .env from template — edit /opt/steadyvox/.env with production values"
else
    echo "  ✓ .env already exists"
fi

# ── Firewall Rules ────────────────────────────────────────
if command -v ufw &>/dev/null; then
    ufw allow 80/tcp    # HTTP / Nginx
    ufw allow 443/tcp   # HTTPS (future)
    ufw allow 22/tcp    # SSH
    ufw allow 9090/tcp  # Prometheus
    ufw allow 3000/tcp  # Grafana
    echo "  ✓ Firewall rules updated"
fi

# ── Start Production Stack ────────────────────────────────
echo ""
echo "[6/6] Starting production stack..."
docker compose -f infra/docker/docker-compose.prod.yml up -d --build

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "13.201.193.223")

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✓ SteadyVox deployed successfully!"
echo "═══════════════════════════════════════════════════════════"
echo "  Web App:    http://${PUBLIC_IP}"
echo "  API Docs:   http://${PUBLIC_IP}/docs"
echo "  Prometheus: http://${PUBLIC_IP}:9090"
echo "  Grafana:    http://${PUBLIC_IP}:3000"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  ⚠ IMPORTANT: Ensure your AWS Security Group allows"
echo "    inbound traffic on ports 80, 443, 9090, 3000"
echo "═══════════════════════════════════════════════════════════"
