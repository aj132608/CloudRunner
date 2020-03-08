echo " ############# Cloning GIT ############# \n "
# Clone the Cloud DSM git repo
sudo git clone https://mohakamg:c469cbaaafe7a1e2b5339f20b360ca9ffc46c649@github.com/aj132608/CloudRunner.git
sudo mv /CloudRunner /.mineai/CloudRunner

echo " ############# Installing Requirements ############# \n "
pip3 install -r /.mineai/CloudRunner/requirements.txt