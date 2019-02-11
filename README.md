# Automated miRDB-search of microRNA targets/seeds in mRNA sequences
This script implements a Selenium WebDriver to automate the access to [miRDB - MicroRNA Target Prediction and Functional Study Database](http://mirdb.org/) and search for microRNAs targets/seeds present in the given mRNA sequences.

## Getting started
 - Mozilla Firefox
 
 You need to have Mozilla Firefox web browser installed and uptaded in your computer, which you can download [here](http://www.mozilla.org).
 - GeckoDriver
 
 Selenium needs GeckoDriver to control the web browser. 
 
 First, [download](https://github.com/mozilla/geckodriver/releases) the compatible GeckoDriver version (32 or 64-bit) with your Mozilla Firefox browser (check with Alt>Help>About).
 
 Then you need to set GeckoDriver into PATH environment variable:

On Windows, go to `Properties>Advanced System Settings>Environment Variables>System Variables>PATH>Edit>New>Paste path to geckodriver.exe`. Or just paste `geckodriver.exe` in some folder already into PATH, like your Python or Anaconda folder.

On Linux, you can run `export PATH=$PATH:/path-to-extracted-file/geckodriver` or simply `sudo mv geckodriver /usr/local/bin/`.

- Requirements
The script needs some Python packages such as: `Selenium`, `Beatiful Soup`, `pandas`. 

You can install them as you wish with `pip install <package>` or `conda install <package>`.

Or you can also install the exact development versions with `pip install -r requirements.txt` or `conda install --file requirements.txt`.
