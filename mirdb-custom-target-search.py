from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from collections import OrderedDict
import pandas as pd
from Bio import SeqIO
import traceback
import argparse

parser = argparse.ArgumentParser(description='Automated miRDB custom microRNA target prediction search: '
                                             '\nThis script uses a webdriver to access the miRDB website and search'
                                             ' for microRNA targets in user given RNA sequences.')
parser.add_argument('inp', type=str, help='Input FASTA file with target sequences')
parser.add_argument('out', type=str, help='Name for output file')
parser.add_argument('sp', type=str, help='Species <Human | Rat | Mouse | Chicken | Dog>')
parser.add_argument('-c', '--cutoff', type=int, help='Score cut-off <int> (default: 80)', default=80)
parser.add_argument('-v', '--visible', action='store_true', help='Shows browser window during the process '
                                                                            '(default: False)', default=False)
args = parser.parse_args()

# Define url
url = 'http://www.mirdb.org/custom.html'

# Define input fasta file
fasta_file = args.inp

# Define output Excel file
output_file = args.out+'.xlsx'

# Options for species: Human, Rat, Mouse, Chicken, Dog
species = args.sp

# Options for submission type: miRNA Sequence, mRNA Target Sequence
submission = 'mRNA Target Sequence'

# Score cut-off
score_cutoff = args.cutoff

# Read sequences
try:
    with open(fasta_file, 'rU') as handle:
        fasta = list(SeqIO.parse(handle, 'fasta'))
        num_seq = len(fasta)
except IOError:
    print('ERROR: could not read file.')

# Instantiates the browser (Firefox is easier to use)
if args.visible:
    firefox = webdriver.Firefox()
else:
    options = Options()
    options.add_argument('--headless')
    firefox = webdriver.Firefox(options=options)


targets_list = []
failed_list = []
try:
    for sequence in range(num_seq):
        failed = OrderedDict()  # OrderedDict() is used to preserve column order when creating dataframe
        if 100 <= len(fasta[sequence]) <= 30000:  # miRDB range restriction

            print('\rSearching targets for sequence: {}/{} - {}'.format(sequence, num_seq, fasta[sequence].id), end='', flush=True)

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
            try:
                firefox.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[3]/form/table/tbody/tr[5]/td/input[1]').click()
            except:
                continue

            # Waits for the results
            timeout = 30
            try:
                result = EC.presence_of_element_located((By.XPATH, '/html/body/form/input[2]'))
                WebDriverWait(firefox, timeout).until(result)
                firefox.find_element_by_xpath('/html/body/form/input[2]').click()
            except TimeoutException:
                print('\nTimed out waiting for {} results.'.format(fasta[sequence].id))
                failed['sequence'] = fasta[sequence].id
                failed['reason'] = 'Timed out waiting for results.'
                failed_list.append(failed)
                continue

            html = firefox.page_source
            soup = BeautifulSoup(html, 'html.parser')  # parses the html with bs4 to scrape data from html tags
            score_list = []
            try:
                rows = soup.find('table', id='table1').find('tbody').find_all('tr')
                # checks in the results table which target scores are equal or greater than the cut-off
                # then saves the indexes in a list
                for i in range(1, len(rows)):
                    cells = rows[i].find_all('td')
                    if int(cells[2].text) >= score_cutoff:
                        score_list.append(i)
            except AttributeError:
                failed['sequence'] = fasta[sequence].id
                failed['reason'] = "Couldn't find table."
                failed_list.append(failed)
                continue

            details = firefox.find_elements_by_name('.submit')  # the first is the "Return" button, the others are "Target Details"

            # only checks the results that passed the cut-off
            for i in score_list:
                try:
                    details[i].click()
                except IndexError:
                    failed['sequence'] = fasta[sequence].id
                    failed['reason'] = 'IndexError: {}'.format(i)
                    failed_list.append(failed)
                    continue

                html = firefox.page_source
                soup = BeautifulSoup(html, 'html.parser')  # parses the html with bs4 to scrape data from html tags

                # usually the score is in cell #7, but sometimes there is an extra row for miRNA previous name
                table = soup.find_all('td')
                try:
                    if table[7].text.isdigit():  # so check if cell #7 text is a digit
                        score = table[7].text
                    else:                       # if it isn't then score should be in cell #9
                        score = table[9].text
                except AttributeError:
                    score = None
                    failed['sequence'] = fasta[sequence].id
                    failed['reason'] = 'Score not found.'

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
            print('\nFailed to search {}. Sequence length out of range ({} nt).'.format(fasta[sequence].id, len(fasta[sequence])))
            failed['sequence'] = fasta[sequence].id
            failed['reason'] = 'Sequence length: {}'.format(len(fasta[sequence]))
            failed_list.append(failed)
except:
    traceback.print_exc()
    print('\nAn exception has occurred. Number of sequences searched until now: {}'.format(sequence))
finally:
    dataframe = pd.DataFrame(targets_list)  # creates a pandas DataFrame("table") with targets information
    dataframe.to_excel(output_file, index=False)  # saves the dataframe to an Excel file
    print('\nResults saved to {}'.format(output_file))
    dataframe_failed = pd.DataFrame(failed_list)
    dataframe_failed.to_excel('failed.xlsx', index=False)
    firefox.close()

