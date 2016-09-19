# Setup

Expand this package after logging into tools.wmflabs.org.

Make sure to have a working environment with pandas 0.18+, oursql and python3. Example commands for setting these up:

    virtualenv venv --system-site-packages --python /usr/bin/python3
    echo 'source $HOME/venv/bin/activate' >> ~/.bash_profile
    source ~/.bash_profile
    pip install pip -U
    pip install https://launchpad.net/oursql/py3k/py3k-0.9.4/+download/oursql-0.9.4.zip
    pip install six pandas==0.18.1 matplotlib==1.4.3 -U

Verify the installations by:

    python -c'import pandas; print(pandas.__version__)'
    python -c'import oursql; print(oursql.__version__)'

# Run

See ./crontab in the top level of the repository.

# Output

![Chart](https://tools.wmflabs.org/commons-app-stats/latest.svg)

More charts are available at http://tools.wmflabs.org/commons-app-stats/.
