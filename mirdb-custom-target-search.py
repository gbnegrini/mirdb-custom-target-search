from selenium import webdriver
from selenium.webdriver.support.ui import Select

# Define url
url = 'http://mirdb.org/miRDB/custom.html'

# Read sequence
try:
    with open('sequence.txt', 'r') as file:
        sequence = file.read()
except IOError:
    print('Could not read file.')

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
select_submission = Select(firefox.find_element_by_name('subChoice'))
select_species.select_by_visible_text(species)
select_submission.select_by_visible_text(submission)

# Enters the sequence in the text field
sequence_field = firefox.find_element_by_name('customSub')
sequence_field.send_keys(sequence)

# Clicks on the "Go" button
firefox.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[3]/form/table/tbody/tr[5]/td/input[1]').click()
# Clicks on the "Retrieve Prediction Result" button
firefox.find_element_by_xpath('/html/body/form/input[2]').click()



