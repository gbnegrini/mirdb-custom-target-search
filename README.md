# Automated miRDB-search of microRNA targets/seeds in mRNA sequences
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgbnegrini%2Fmirdb-custom-target-search.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fgbnegrini%2Fmirdb-custom-target-search?ref=badge_shield)

This script implements a Selenium WebDriver to automate the access to [miRDB - MicroRNA Target Prediction and Functional Study Database](http://mirdb.org/) and search for microRNAs targets/seeds present in custom mRNA sequences.

## Requirements

- Mozilla Firefox
 
  - You need to have Mozilla Firefox web browser installed and uptaded in your computer, which you can download [here](http://www.mozilla.org).

- Python
  - version 3

- Packages and libraries
  - geckodriver
  - openpyxl
  - biopython
  - selenium
  - pandas
  - beautifulsoup4

You can easily install packages and libraries by creating a conda environment with:

 `conda env create -f requirements.yml`. 

If so, don't forget to activate the environment with `conda activate mirdb-search` before running the script.

## Running the script


```
python mirdb_custom_target_search.py [-h] [-c CUTOFF] [-v]
                                     inp out {Human,Rat,Mouse,Chicken,Dog}


positional arguments:
  inp                   Input FASTA file with target sequences
  out                   Name for output file
  {Human,Rat,Mouse,Chicken,Dog}
                        Species

optional arguments:
  -h, --help            show this help message and exit
  -c CUTOFF, --cutoff CUTOFF
                        Score cut-off <int> (default: 80)
  -v, --visible         Shows browser window during the process (default:
                        False)

```

## Example:
```
./python mirdb-custom-target-search.py test_data.fa test Human
```

### Output
|             sequence             | score | seeds |          mirna             |
| -------------------------------- | ----- |--------|----------------------------|
| NC_000010.11:87823625-87833625 |  96   |   10    |      hsa-miR-5692a          |
| NC_000010.11:87823625-87833625 |94 |9 |hsa-miR-3613-3p|
...|...|...|...|

## References
- Weijun Liu and Xiaowei Wang (2019) Prediction of functional microRNA targets by integrative modeling of microRNA binding and target expression data. Genome Biology. 20:18.
- Nathan Wong and Xiaowei Wang (2015) miRDB: an online resource for microRNA target prediction and functional annotations. Nucleic Acids Research. 43(D1):D146-152.


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgbnegrini%2Fmirdb-custom-target-search.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fgbnegrini%2Fmirdb-custom-target-search?ref=badge_large)