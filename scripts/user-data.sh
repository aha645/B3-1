#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
cat > /etc/apt/sources.list.d/docker.sources <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
install -d -m 0755 /home/ubuntu/web-lab/html
cat > /home/ubuntu/web-lab/html/index.html <<'EOF'
<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>AWS Web Lab</title></head>
<body><h1>Hello Cloud</h1><p>Docker Nginx로 서비스 중입니다.</p></body></html>
EOF
printf 'OK\n' > /home/ubuntu/web-lab/html/health
chmod 0644 /home/ubuntu/web-lab/html/index.html /home/ubuntu/web-lab/html/health
chown -R ubuntu:ubuntu /home/ubuntu/web-lab
docker run -d --name web-lab-nginx --restart unless-stopped -p 80:80 \
  --mount type=bind,source=/home/ubuntu/web-lab/html,target=/usr/share/nginx/html,readonly nginx:stable
for attempt in {1..30}; do
  if curl -fsS http://localhost/health; then exit 0; fi
  sleep 2
done
exit 1
