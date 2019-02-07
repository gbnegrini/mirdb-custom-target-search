from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from collections import OrderedDict
import pandas as pd
from Bio import SeqIO

# Define url
url = 'http://mirdb.org/miRDB/custom.html'

# Define input fasta file
fasta_file = 'SRA_circRNAs.uniq.fa'

# Define output Excel file
output_file = 'custom_target_search.xlsx'

# Define number of sequences to search
num_seq = 5

# Options for species: Human, Rat, Mouse, Chicken, Dog
species = 'Human'

# Options for submission type: miRNA Sequence, mRNA Target Sequence
submission = 'mRNA Target Sequence'

# Read sequences
try:
    with open(fasta_file, 'rU') as handle:
        fasta = list(SeqIO.parse(handle, 'fasta'))
except IOError:
    print('ERROR: could not read file.')

# Instantiates the browser (Firefox is easier to use)
firefox = webdriver.Firefox()
targets_list = []
for sequence in range(0, num_seq):

    # Gets the desired page
    firefox.get(url)

    # Selects the options
    select_species = Select(firefox.find_element_by_name('searchSpecies'))
    select_species.select_by_visible_text(species)
    select_submission = Select(firefox.find_element_by_name('subChoice'))
    select_submission.select_by_visible_text(submission)

    # Enters the sequence in the text field
    sequence_field = firefox.find_element_by_name('customSub')
    sequence_field.send_keys(fasta[sequence])

    # Clicks on the "Go" button
    firefox.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[3]/form/table/tbody/tr[5]/td/input[1]').click()
    # Waits for the results
    time.sleep(1)
    # Clicks on the "Retrieve Prediction Result" button
    firefox.find_element_by_xpath('/html/body/form/input[2]').click()

    details = firefox.find_elements_by_name('.submit')  # the first is the "Return" button, the others are "Target Details"

    # loops through all targets
    for i in range(1, len(details)):
        details[i].click()
        html = firefox.page_source
        soup = BeautifulSoup(html, 'html.parser')  # parses the html with bs4 to scrape data from html tags
        seeds = soup.find_all('font', {'color': '#0000FF'})  # find seeds by color
        number_of_seeds = len(seeds)
        links = soup.find_all('a', href=True)
        mirna_link = 'www.mirdb.org'+links[1]['href']  # builds a link for the miRNA page
        mirna_name = links[1].font.text  # gets miRNA name

        # usually the score is in cell #7, but sometimes there is an extra row for miRNA previous name
        table = soup.find_all('td')
        if table[7].text.isdigit():  # so check if cell #7 text is a digit
            score = table[7].text
        else:                       # if it isn't then score should be in cell #9
            score = table[9].text

        # stores the above information in a dictionary
        targets_info = OrderedDict()  # OrderedDict() is used to preserve column order when creating dataframe
        targets_info['sequence'] = fasta[sequence].id
        targets_info['score'] = score
        targets_info['#seeds'] = number_of_seeds
        targets_info['mirna'] = mirna_name
        targets_info['link'] = mirna_link

        # adds the dictionary to a list of dictionaries containing the target's data
        targets_list.append(targets_info)

        print('Sequence: {}'.format(fasta[sequence].id))
        print('Number of seeds: {}'.format(number_of_seeds))
        print('miRNA link: {}'.format(mirna_link))
        print('miRNA name: {}'.format(mirna_name))
        print('Score: {}'.format(score))
        print('-------------------------------------')

        firefox.back()  # goes back to prediction page
        details = firefox.find_elements_by_name('.submit')  # find all buttons again

dataframe = pd.DataFrame(targets_list)  # creates a pandas DataFrame("table") with targets information
dataframe.to_excel(output_file, index=False)  # saves the dataframe to an Excel file
firefox.close()

