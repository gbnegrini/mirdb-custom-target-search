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

## Running the script
- Usage:
```
./python mirdb-custom-target-search.py [-h] [-c CUTOFF] [-v] inp out sp

positional arguments:
  inp                   Input FASTA file with target sequences
  out                   Name for output file
  sp                    Species <Human | Rat | Mouse | Chicken | Dog>

optional arguments:
  -h, --help            show this help message and exit
  -c CUTOFF, --cutoff CUTOFF
                        Score cut-off <int> (default: 80)
  -v, --visible         Shows browser window during the process (default:
                        False)

```

The code generates two `.xlsx` output files: one contains the data related to each mRNA sequence provided (sequence name, target score, number of seeds, microRNA name and microRNA info page link) and the other (`failed.xlsx`) is a record of which sequences coundn't be search, most commonly due to miRDB sequence lenght limitation (100 to 30,000 bases long).

- Example:
```
./python mirdb-custom-target-search.py my_sequences.fa my_sequences_out Human
```

|             sequence             | score | #seeds |          mirna             |                           link                           |
| -------------------------------- | ----- |--------|----------------------------|----------------------------------------------------------|
| circRNA__15_68141945-68146700(+) |  92   |   3    |      hsa-miR-4306          |www.mirdb.org/cgi-bin/mature_mir.cgi?name=hsa-miR-4306|



## References
- Weijun Liu and Xiaowei Wang (2019) Prediction of functional microRNA targets by integrative modeling of microRNA binding and target expression data. Genome Biology. 20:18.
- Nathan Wong and Xiaowei Wang (2015) miRDB: an online resource for microRNA target prediction and functional annotations. Nucleic Acids Research. 43(D1):D146-152.
