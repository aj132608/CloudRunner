# Install Docker
sudo apt-get -y remove docker docker-engine docker.io
sudo apt install -y docker.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
#sudo apt install -y docker-compose
#sudo apt update -y docker-compose
