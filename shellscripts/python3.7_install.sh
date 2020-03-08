echo " ############# Installing Python ############# \n "

sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.7

echo " ############# Installing PIP ############# \n "
sudp apt install -y python3-pip