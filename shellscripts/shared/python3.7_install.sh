echo " ############# Installing Python ############# \n "

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.7

echo " ############# Installing PIP ############# \n "
apt install -y python3-pip
python3.7 -m pip install --upgrade pip