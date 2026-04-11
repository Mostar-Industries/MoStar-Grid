#!/bin/bash
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y unzip

echo "Installing bun..."
curl -fsSL https://bun.sh/install | bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

echo "Installing cloudflared..."
sudo curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

echo '=== Bun ==='
$BUN_INSTALL/bin/bun --version 2>/dev/null || echo MISSING
echo '=== Cloudflared ==='
cloudflared --version 2>/dev/null || echo MISSING
