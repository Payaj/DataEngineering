import re
import cv2
import time
import pytesseract
import numpy as np
import pandas as pd
from PIL import Image as PI
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Extra Url in case of error
# https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageVtu?searchCriteriaStringValue=%7B%22hid_last%22%3Anull%2C%22
# hid_first%22%3Anull%2C%22hid_ml%22%3Anull%2C%22hid_suffix%22%3Anull%2C%22hid_business%22%3Anull%2C%22hid_partype%22%3
# Anull%2C%22hid_partype_name%22%3Anull%2C%22hid_selectdate%22%3Anull%2C%22hid_datefromm%22%3Anull%2C%22hid_datefromd%
# 22%3Anull%2C%22hid_datefromy%22%3Anull%2C%22hid_datetom%22%3Anull%2C%22hid_datetod%22%3Anull%2C%22hid_datetoy%22%3
# Anull%2C%22hid_borough%22%3A0%2C%22hid_doctype%22%3Anull%2C%22hid_sort%22%3Anull%2C%22hid_doctype_name%22%3Anull%2C%
# 22hid_borough_name%22%3Anull%2C%22hid_block%22%3A0%2C%22hid_block_value%22%3Anull%2C%22hid_lot%22%3A0%2C%22hid_lot_
# value%22%3Anull%2C%22hid_unit%22%3Anull%2C%22hid_filenbr%22%3Anull%2C%22hid_CRFN%22%3Anull%2C%22hid_DocID%22%3A%2220
# 19040900053001%22%2C%22hid_year%22%3A0%2C%22hid_reel%22%3A0%2C%22hid_TransID%22%3Anull%2C%22FormatedToDate%22%3Anull%
# 2C%22FormatedFromDate%22%3Anull%2C%22UserType%22%3Anull%2C%22hid_TotalPages%22%3A11%2C%22ListBoroughs%22%3Anull%2C%22
# ListDocumentTypes%22%3Anull%2C%22ListDocumentClass%22%3Anull%2C%22DisplaySearchResultLink%22%3Afalse%2C%22CoverPage
# MainOptionURL%22%3A%22https%3A%2F%2Fa836-acris.nyc.gov%2FCP%2FCoverPage%2FMainMenu%22%2C%22AddressParcelLookUpURL%22%
# 3Anull%2C%22PagerViewModel%22%3Anull%2C%22DisplayNYCLink%22%3Atrue%2C%22hid_reel_page%22%3A0%2C%22hid_cur_page%22%3A1
# %2C%22hid_error%22%3Anull%2C%22hid_DrpTolPage1%22%3A0%2C%22hid_DrpTolPage2%22%3A0%2C%22hid_DrpTolPage3%22%3A0%2C%22hid
# _DrpTolPage4%22%3A0%2C%22SearchResults%22%3Anull%2C%22hid_ReqID%22%3Anull%2C%22hid_SearchType%22%3Anull%2C%22hid_
# ISIntranet%22%3A%22N%22%2C%22hid_ISPATUser%22%3Afalse%2C%22hid_max_rows%22%3A0%2C%22hid_page%22%3A0%7D&doc_id=201904
# 0900053001

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.0.0_1/bin/tesseract'


def browser_setting(proxy_new, path_to_driver):
    proxy = {'address': proxy_new + '.proxymesh.com:31280',
             'username': 'topagenets',
             'password': 'Topagents1'}

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
    brow = webdriver.Chrome(executable_path=path_to_driver, chrome_options=options,
                            desired_capabilities=capabilities)
    return brow


def doc_identification(path_to_doc_img):
    print('Searching page...')
    start = time.time()
    img_rgb = cv2.imread(path_to_doc_img)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    template = cv2.imread('temp.png', 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.4
    loc = np.where(res >= threshold)

    end = time.time()
    print('Search took {} seconds'.format(end - start))

    if len(loc[0]) > 0:
        return True

    return False


def ocr(path_to_doc_img):

    img = cv2.imread(path_to_doc_img)
    roi = img[1000:1186, 0:540].copy()
    roi_path = path_to_doc_img[:-4] + '_roi.png'
    cv2.imwrite(roi_path, roi)

    text = pytesseract.image_to_string(PI.open(roi_path))

    return text


headers = {'User-agent': 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ '
                         '(KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3'}
proxies = {'http': 'http://topagenets:Trustscout1@us.proxymesh.com:31280',
           'https': 'http://topagenets:Trustscout1@us.proxymesh.com:31280'}
path_to_chrome_driver = '/Users/payaj/chromedriver'
available_proxies = ['us-ny', 'us-fl', 'us-wa', 'de', 'us-dc', 'us-ca', 'au', 'nl', 'sg', 'uk', 'us']

browser = browser_setting(proxy_new=available_proxies[-1], path_to_driver=path_to_chrome_driver)

base_url = 'https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id='

browser.set_window_position(0, 0)
browser.set_window_size(640, 716)
size = browser.get_window_size()
print("Window size: width = {}px, height = {}px.".format(size["width"], size["height"]))

doc_ids = [2015121700217001, 2015082801341001, 2016041900781001, 2015082801341001, 2018110901058001]

date_pd = pd.DataFrame(columns=['document_id', 'date'])

for doc_id in doc_ids:

    browser.get(url=base_url+str(doc_id))
    browser.switch_to.frame('mainframe')

    while True:
        browser.save_screenshot('page.png')
        match = doc_identification('page.png')
        if match:
            print('Document found...')

            time.sleep(1)
            browser.find_element_by_xpath('//*[@id="vtm_main"]/div[1]/table/tbody/tr/td[4]').click()
            for i in range(6):
                browser.find_element_by_xpath('//*[@id="vtm_main"]/div[1]/table/tbody/tr/td[5]/img').click()

            browser.save_screenshot('/Users/payaj/PycharmProjects/opencv_test/acris_jpeg/' + str(doc_id) + '.png')
            break
        else:
            browser.find_element_by_xpath('//*[@id="vtm_main"]/div[1]/table/tbody/tr/td[2]/img').click()
            time.sleep(1)

    date_text = ocr('/Users/payaj/PycharmProjects/opencv_test/acris_jpeg/' + str(doc_id) + '.png')

    date_text = date_text.strip().replace('\n', '').split('/')
    for i in range(len(date_text)):
        date_text[i] = re.sub('[^0-9]', '', date_text[i])

    date_text = '/'.join(date_text)

    date_pd = date_pd.append({'document_id': str(doc_id) + 't', 'date': date_text}, ignore_index=True)


date_pd.to_csv('test_dates.csv')
