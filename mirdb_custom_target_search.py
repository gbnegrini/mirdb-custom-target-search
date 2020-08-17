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
import argparse
import logging
import sqlite3

class MirdbSearch():
    def __init__(self, fasta, species, cutoff):
        self.url = 'http://www.mirdb.org/custom.html'
        self.fasta = self._open_fasta(fasta)
        self.species = species
        self.submission = 'mRNA Target Sequence'
        self.cutoff = cutoff
    
    def _open_fasta(self, fasta) -> list:
        try:
            with open(fasta) as handle:
                return list(SeqIO.parse(handle, 'fasta'))
        except IOError:
            logging.exception("Could not read file.")
            raise IOError("Could not read file.")

class Crawler():
    def __init__(self, visible):
        self.driver = self._create_driver(visible)
    
    def _create_driver(self, visible):
        if args.visible:
            return webdriver.Firefox()
        else:
            options = Options()
            options.add_argument('--headless')
            return webdriver.Firefox(options=options)
    
    def select_element(self, name, value):
        select = Select(self.driver.find_element_by_name(name))
        select.select_by_visible_text(value)
    
    def enter_sequence(self, sequence):
        self.driver.find_element_by_name('customSub').send_keys(sequence)
    
    def continue_to_results(self):
        try:
            self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td[3]/form/table/tbody/tr[5]/td/input[1]').click()
        except:
            pass

    def wait_results(self):
        timeout = 30
        result = EC.presence_of_element_located((By.XPATH, '/html/body/form/input[2]'))
        try:
            WebDriverWait(self.driver, timeout).until(result)
            self.driver.find_element_by_xpath('/html/body/form/input[2]').click()
        except TimeoutError:
            logging.exception("TimeoutError")

class Scraper():
    def __init__(self):
        self.soup = None
    
    def parse(self, page):
        self.soup = BeautifulSoup(page, 'html.parser')
    
    def get_above_cutoff(self, cutoff):
        passed_cutoff = []
        rows = self.soup.find('table', id='table1').find('tbody').find_all('tr')
        for i in range(1, len(rows)):
            try:
                cells = rows[i].find_all('td')
                if int(cells[2].text) >= cutoff:
                    passed_cutoff.append(i)
            except AttributeError:
                logging.exception("AttributeError")
                pass
        return passed_cutoff
    
    def get_score(self):
        # usually the score is in cell #7, but sometimes there is an extra row for miRNA previous name
        table = self.soup.find_all('td')
        try:
            if table[7].text.isdigit():  # so check if cell #7 text is a digit
                score = table[7].text
            else:                       # if it isn't then score should be in cell #9
                score = table[9].text
        except AttributeError:
            logging.exception("AttributeError")
        return score
    
    def get_number_of_seeds(self):
        seeds = self.soup.find_all('font', {'color': '#0000FF'})  # find seeds by text color
        try:
            number_of_seeds = len(seeds)
        except AttributeError:
            number_of_seeds = None
        return number_of_seeds
    
    def get_mirna_name(self):
        links = scraper.soup.find_all('a', href=True)
        try:
            mirna_name = links[1].font.text
        except AttributeError:
            mirna_name = None
        return mirna_name

class Target():
    def __init__(self):
        self.sequence = None
        self.score = None
        self.number_of_seeds = None
        self.mirna_name = None

class Database():
    def __init__(self, database: str):
        self.__connection = sqlite3.connect(database)
        self.__create_tables()

    @property
    def connection(self) -> sqlite3.Connection:
        return self.__connection
    
    def __execute_query(self, *args) -> list:
        try:
            cursor = self.connection.cursor()
            cursor.execute(*args)
            self.connection.commit()
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result

    def __create_tables(self):
        self.__execute_query("""
        CREATE TABLE IF NOT EXISTS targets (
        sequence TEXT,
        score INTEGER,
        seeds INTEGER,
        mirna TEXT
    );""")

    def insert_target(self, target: Target):
        self.__execute_query("""INSERT INTO targets (sequence, score, seeds, mirna)
                                    VALUES (?,?,?,?)""",
                            [target.sequence,target.score,target.number_of_seeds,target.mirna_name])
    
    def export_to_csv(self, output_name: str):
        table = pd.read_sql_query("SELECT * FROM targets", self.connection)
        table.to_csv(output_name, index=None, header=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated miRDB custom microRNA target prediction search: '
                                                '\nThis script uses a webdriver to access the miRDB website and search'
                                                ' for microRNA targets in user given RNA sequences.')
    parser.add_argument('inp', type=str, help='Input FASTA file with target sequences')
    parser.add_argument('out', type=str, help='Name for output file')
    parser.add_argument('sp', type=str, choices=["Human","Rat","Mouse","Chicken", "Dog"], help='Species')
    parser.add_argument('-c', '--cutoff', type=int, help='Score cut-off <int> (default: 80)', default=80)
    parser.add_argument('-v', '--visible', action='store_true', help='Shows browser window during the process '
                                                                                '(default: False)', default=False)
    args = parser.parse_args()
    logging.basicConfig(filename="mirdb_error.log",format='%(asctime)s - %(message)s', level=logging.INFO)

    search = MirdbSearch(args.inp,args.sp,args.cutoff)
    crawler = Crawler(args.visible)
    scraper = Scraper()
    database = Database(f'{args.out}.db')
    
    try:
        for n, sequence in enumerate(search.fasta):
            if 100 <= len(sequence.seq) <= 30000:  # miRDB range restriction
                print(f'\rSearching targets for sequence: {n+1}/{len(search.fasta)} - {sequence.id}', end='', flush=True)
                crawler.driver.get(search.url)
                crawler.select_element('searchSpecies', search.species)
                crawler.select_element('subChoice', search.submission)
                crawler.enter_sequence(sequence.seq)
                crawler.continue_to_results()
                crawler.wait_results()
                html = crawler.driver.page_source
                scraper.parse(html)
                passed_cutoff_rows = scraper.get_above_cutoff(search.cutoff)

                for row in passed_cutoff_rows:
                    details = crawler.driver.find_elements_by_name('.submit')  # the first is the "Return" button, the others are "Target Details"
                    try:
                        details[row].click()
                    except IndexError:
                        logging.exception(f"{sequence.id}")
                        continue
                    html = crawler.driver.page_source
                    scraper.parse(html)
                    target = Target()
                    target.sequence = sequence.id
                    target.score = scraper.get_score()
                    target.number_of_seeds = scraper.get_number_of_seeds()
                    target.mirna_name = scraper.get_mirna_name()
                    database.insert_target(target)
                    crawler.driver.back()
            else:
                print(f'\nFailed to search {sequence.id}. Sequence length out of range ({len(sequence)} nt).')
                logging.exception(f"{sequence.id}\t{len(sequence)}")
    except:
        logging.exception("Error")
        print(f'\nAn exception has occurred while searching: {sequence.id}')
    finally:
        database.export_to_csv(f'{args.out}.csv')
        print(f'\nResults saved to {args.out}.csv')
        crawler.driver.close()
        database.connection.close