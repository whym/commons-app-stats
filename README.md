# Setup

Make sure pandas 0.18+ and python3 working:

``
virtualenv venv --system-site-packages --python /usr/bin/python3
echo 'source $HOME/venv/bin/activate' >> ~/.bash_profile
source ~/.bash_profile
pip install pip -U
pip install https://launchpad.net/oursql/py3k/py3k-0.9.4/+download/oursql-0.9.4.zip
pip install six pandas==0.18.1 matplotlib==1.4.3 -U
``

