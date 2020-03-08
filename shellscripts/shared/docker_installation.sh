# Install Docker
sudo apt-get -y remove docker docker-engine docker.io
sudo apt install -y docker.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
