from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from collections import OrderedDict
import pandas as pd

# Define url
url = 'http://mirdb.org/miRDB/custom.html'

# Read sequence
try:
    with open('sequence.txt', 'r') as file:
        sequence = file.read()
except IOError:
    print('ERROR: could not read file.')

# Options for species: Human, Rat, Mouse, Chicken, Dog
species = 'Human'

# Options for submission type: miRNA Sequence, mRNA Target Sequence
submission = 'mRNA Target Sequence'

# Instantiates the browser (Firefox is easier to use)
firefox = webdriver.Firefox()

# Gets the desired page
firefox.get(url)

# Selects the options
select_species = Select(firefox.find_element_by_name('searchSpecies'))
select_species.select_by_visible_text(species)
select_submission = Select(firefox.find_element_by_name('subChoice'))
select_submission.select_by_visible_text(submission)

# Enters the sequence in the text field
sequence_field = firefox.find_element_by_name('customSub')
sequence_field.send_keys(sequence)

# Clicks on the "Go" button
firefox.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[3]/form/table/tbody/tr[5]/td/input[1]').click()
# Waits for the results
time.sleep(1)
# Clicks on the "Retrieve Prediction Result" button
firefox.find_element_by_xpath('/html/body/form/input[2]').click()

details = firefox.find_elements_by_name('.submit')  # the first is the "Return" button, the others are "Target Details"

targets_list = []

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
    targets_info['sequence'] = 'test{}'.format(i)
    targets_info['score'] = score
    targets_info['#seeds'] = number_of_seeds
    targets_info['mirna'] = mirna_name
    targets_info['link'] = mirna_link

    # adds the dictionary to a list of dictionaries containing the target's data
    targets_list.append(targets_info)


    print('Number of seeds: {}'.format(number_of_seeds))
    print('miRNA link: {}'.format(mirna_link))
    print('miRNA name: {}'.format(mirna_name))
    print('Score: {}'.format(score))
    print('-------------------------------------')

    firefox.back()  # goes back to prediction page
    details = firefox.find_elements_by_name('.submit')  # find all buttons again

dataframe = pd.DataFrame(targets_list)  # creates a pandas DataFrame("table") with targets information
dataframe.to_excel('custom_target_search.xlsx', index=False)  # saves the dataframe to an Excel file
firefox.close()

