This is the source code of a web service hosted by tools.wmflabs.org. It shows charts indicating the number of files upload using the Android app for Wikimedia Commons. It is entirely written in Python.

All the data is extracted from the central database of Wikimedia Commons *using an access that allows retrieving publicly accessible data only.* In other words, this just gives a graphical summary of publicly accessible data such as the chronological list of all mobile uploads -- if a photo has not been uploaded, that won't be counted here either.

# Setup

Expand this package after logging into tools.wmflabs.org.

Make sure to have a working environment with pandas etc. (See ``requirements.txt`` for details.) Example commands for setting these up:

    virtualenv venv --system-site-packages --python /usr/bin/python3
    echo 'source $HOME/venv/bin/activate' >> ~/.bash_profile
    source ~/.bash_profile
    pip install pip -U
    pip install -r requirements.txt

Verify the installations by:

    python -c'import pandas; print(pandas.__version__)'

# Run

See ./crontab in the top level of the repository.

# Output

![Chart](https://tools.wmflabs.org/commons-app-stats/latest.svg)

More charts are available at http://tools.wmflabs.org/commons-app-stats/.
