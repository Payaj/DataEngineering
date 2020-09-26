#!/usr/local/bin/python3.6

import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

# this goes to the top of the script
dirPath = '/Users/payaj/Downloads/'

new_dir = dirPath + 'pdfs'
files = os.listdir(dirPath)
if new_dir.split('/')[-1] not in files:
    os.makedirs(new_dir)

# this goes after we define the option in the script for selenium


docDict = {}
docPaths = []
docIDs = []
baseURL = "http://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id="
apiEndpoint = "https://api.ocr.space/parse/image"
key = "XXXXXXX"#Space OCR API key

path_to_chromedriver = '/Users/payaj/chromedriver'

proxy = {'address': 'XXXX',
         'username': 'XXXX',
         'password': 'XXXX'}#if not using proxy ips then no need to use DesiredCapabilities below: 

capabilities = dict(DesiredCapabilities.CHROME)
capabilities['proxy'] = {'proxyType': 'MANUAL',
                         'httpProxy': proxy['address'],
                         'ftpProxy': proxy['address'],
                         'sslProxy': proxy['address'],
                         'noProxy': '',
                         'class': "org.openqa.selenium.Proxy",
                         'autodetect': False}

capabilities['proxy']['socksUsername'] = proxy['username']
capabilities['proxy']['socksPassword'] = proxy['password']

options = webdriver.ChromeOptions()
prefs = {'download.default_directory': dirPath + new_dir}
options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=options,
                          desired_capabilities=capabilities)




"""
Retrieve Acris document ID's from JSON
:param filepath: File location (not relative to CWD)
"""


def getDocumentIDs(filepath):
    # with open(filepath) as docFile:
    #     documents = json.load(docFile)
    document = pd.read_csv('~/Downloads/ACRIS_-_Real_Property_Master.csv', dtype='unicode')
    document = document.rename(index=str, columns={'DOCUMENT ID': 'document_id'})
    # for i in range(len(document)):
    #     docIDs.append(document.loc[i, "DOCUMENT_ID"])

    for ids in document['document_id']:
        docIDs.append(ids)

"""
Visit document page and download PDF
:param filepath: File location (not relative to CWD)
"""


# doc_id = docIDs[0]
def downloadPDF(doc_id):

    #Let driver wait to avoid race conditions
    driver.get(baseURL + doc_id)
    driver.implicitly_wait(20)

    driver.switch_to.frame('mainframe')

    #Open save window
    # driver.find_element_by_xpath('//img[@title="Save"]').click()
    driver.find_elements_by_class_name("vtm_buttonCell")[-1].click()
    driver.implicitly_wait(20)

    #Select only first page and click download
    # driver.find_element_by_class_name('vtmBtn').click()
    driver.find_elements_by_class_name("vtm_exportDialogPageRangeRadio")[-1].click()
    # driver.find_element_by_xpath('//*[@id="vtm_printOK"]').click()
    time.sleep(1)

    driver.find_elements_by_class_name("vtmBtn")[0].click()

    #Save file name
    newPdfLocation = "'" + doc_id + "&page (1).pdf'"
    docPaths.append(newPdfLocation)
    print("Expected file path: acris/input/" + newPdfLocation)	#FOR DEBUG


if __name__ == '__main__':
    getDocumentIDs("~/Downloads/ACRIS_-_Real_Property_Master.csv") #Sample input

    for d in docIDs:
        downloadPDF(d)

    # docDict['paths'] = docPaths

    #Export paths to JSON
    # os.chdir('../input')
    # with open('documentPaths.json', 'w+') as pathFile:
    #     json.dump(docDict, pathFile)
    # os.chdir('../scripts')
    #
    # print "Number of documents downloaded: " + str(len(docIDs)) + "\n"    #FOR DEBUG
