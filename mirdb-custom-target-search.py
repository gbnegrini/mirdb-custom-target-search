from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
from bs4 import BeautifulSoup
from collections import OrderedDict
import pandas as pd
from Bio import SeqIO
import traceback

# Define url
url = 'http://mirdb.org/miRDB/custom.html'

# Define input fasta file
fasta_file = 'SRA_circRNAs.uniq.fa'

# Define output Excel file
output_file = 'custom_target_search.xlsx'

# Define number of sequences to search
num_seq = 200

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
options = Options()
options.add_argument('--headless')
#firefox = webdriver.Firefox(options=options)
firefox = webdriver.Firefox()

targets_list = []
try:
    for sequence in range(0, num_seq):
        if 100 <= len(fasta[sequence]) <= 30000:  # miRDB range restriction

            print('\rSearching targets for sequence: #{} - {}'.format(sequence, fasta[sequence].id), end='', flush=True)

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
            timeout = 30
            try:
                result = EC.presence_of_element_located((By.XPATH, '/html/body/form/input[2]'))
                WebDriverWait(firefox, timeout).until(result)
                firefox.find_element_by_xpath('/html/body/form/input[2]').click()
            except TimeoutException:
                print('\nTimed out waiting for {} results.'.format(fasta[sequence].id))
                break

            time.sleep(2)
            details = firefox.find_elements_by_name('.submit')  # the first is the "Return" button, the others are "Target Details"

            # loops through all targets
            for i in range(1, len(details)):
                try:
                    details[i].click()
                except IndexError:
                    break
                html = firefox.page_source
                soup = BeautifulSoup(html, 'html.parser')  # parses the html with bs4 to scrape data from html tags
                seeds = soup.find_all('font', {'color': '#0000FF'})  # find seeds by color
                try:
                    number_of_seeds = len(seeds)
                except AttributeError:
                    number_of_seeds = None
                links = soup.find_all('a', href=True)
                try:
                    mirna_link = 'www.mirdb.org'+links[1]['href']  # builds a link for the miRNA page
                except AttributeError:
                    mirna_link = None
                try:
                    mirna_name = links[1].font.text  # gets miRNA name
                except AttributeError:
                    mirna_name = None

                # usually the score is in cell #7, but sometimes there is an extra row for miRNA previous name
                table = soup.find_all('td')
                try:
                    if table[7].text.isdigit():  # so check if cell #7 text is a digit
                        score = table[7].text
                    else:                       # if it isn't then score should be in cell #9
                        score = table[9].text
                except AttributeError:
                    score = None

                # stores the above information in a dictionary
                targets_info = OrderedDict()  # OrderedDict() is used to preserve column order when creating dataframe
                targets_info['sequence'] = fasta[sequence].id
                targets_info['score'] = score
                targets_info['#seeds'] = number_of_seeds
                targets_info['mirna'] = mirna_name
                targets_info['link'] = mirna_link

                # adds the dictionary to a list of dictionaries containing the target's data
                targets_list.append(targets_info)

                firefox.back()  # goes back to prediction page
                details = firefox.find_elements_by_name('.submit')  # find all buttons again
        else:
            print('\nFailed to search {}. Sequence length exceeded ({} nt).'.format(fasta[sequence].id, len(fasta[sequence])))
except:
    traceback.print_exc()
    print('\nAn exception has occurred. Number of sequences searched until now: {}'.format(sequence))
finally:
    dataframe = pd.DataFrame(targets_list)  # creates a pandas DataFrame("table") with targets information
    dataframe.to_excel(output_file, index=False)  # saves the dataframe to an Excel file
    print('\nResults saved to {}'.format(output_file))
    #firefox.close()

