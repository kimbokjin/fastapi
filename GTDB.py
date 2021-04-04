import time
import csv
import pandas as pd
import openpyxl
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display


def Get_accession_number(excel_file, outgroup=None):

    path = "/home/bokjin"
    # os.chdir(path)
    selenium_path = "/usr/bin/chromedriver"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    chrome_options.add_argument("window-size=1920x1080")

    browser = webdriver.Chrome(selenium_path, chrome_options=chrome_options)
    browser.get("https://gtdb.ecogenomic.org/")
    vaild_file_1 = pd.read_excel(f"{excel_file}", engine="openpyxl")
    #outgroup = "Psychromonas arctica"
    sp_name = vaild_file_1["Name"]
    ncbi_sp_name = []
    ncbi_id = []
    id = []
    range_list = range(1, len(sp_name) + 1)

    for j, k in zip(sp_name, range_list):
        try:
            elem = browser.find_element_by_name('keywrd')
            elem.send_keys(j)
            elem_2 = browser.find_element_by_xpath('//*[@id="btnSearchForm"]')
            elem_2.click()
            WebDriverWait(browser, timeout=10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="results"]/tbody/tr[1]')))
            elem_3 = browser.find_element_by_id('filterstrain')
            elem_3.click()
            class_odd = browser.find_elements_by_class_name("odd")
            class_even = browser.find_elements_by_class_name("even")
            tr_range = range(1, len(class_even) + len(class_odd))

            for i in tr_range:
                tr_name = browser.find_element_by_xpath(
                    f'//*[@id="results"]/tbody/tr[{i}]/td[2]').text
                GTDB = browser.find_element_by_xpath(
                    f'//*[@id="results"]/tbody/tr[{i}]/td[5]').text
                NCBI = browser.find_element_by_xpath(
                    f'//*[@id="results"]/tbody/tr[{i}]/td[6]').text
                ID = browser.find_element_by_xpath(
                    f'//*[@id="results"]/tbody/tr[{i}]/td[1]/a').text
                if j in tr_name and NCBI == "yes":
                    ncbi_sp_name.append(j)
                    ncbi_id.append(ID)
                    id.append(ID)
                    break
                elif i == len(class_even) + len(class_odd) - 1:
                    id.append("None")
                else:
                    continue
        except Exception as error:
            print(error)
            id.append("None")

    try:
        elem = browser.find_element_by_name('keywrd')
        elem.send_keys(outgroup)
        elem_2 = browser.find_element_by_xpath('//*[@id="btnSearchForm"]')
        elem_2.click()
        WebDriverWait(browser, timeout=10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="results"]/tbody/tr[1]')))
        elem_3 = browser.find_element_by_id('filterstrain')
        elem_3.click()
        class_odd = browser.find_elements_by_class_name("odd")
        class_even = browser.find_elements_by_class_name("even")
        tr_range = range(1, len(class_even) + len(class_odd))

        for i in tr_range:
            tr_name = browser.find_element_by_xpath(
                f'//*[@id="results"]/tbody/tr[{i}]/td[2]').text
            GTDB = browser.find_element_by_xpath(
                f'//*[@id="results"]/tbody/tr[{i}]/td[5]').text
            NCBI = browser.find_element_by_xpath(
                f'//*[@id="results"]/tbody/tr[{i}]/td[6]').text
            ID = browser.find_element_by_xpath(
                f'//*[@id="results"]/tbody/tr[{i}]/td[1]/a').text
            if outgroup in tr_name and NCBI == "yes":
                ncbi_sp_name.append(outgroup)
                ncbi_id.append(ID)
                id.append(ID)
                break
            elif i == len(class_even) + len(class_odd) - 1:
                print("None ID")
            else:
                continue
    except Exception as error:
        print(error)

    id_df_1 = pd.DataFrame({"SP_NAME": ncbi_sp_name, "ID": ncbi_id})
    id_df_1.to_csv("SP_ID_list.txt", index=False, header=True)
    id_df_2 = pd.DataFrame(ncbi_id)
    id_df_2.to_csv("ID_list.txt", index=False, header=False)
    id_dataframe = pd.DataFrame({"ID": id})
    result = pd.concat([vaild_file_1, id_dataframe], axis=1)
    result.to_excel("ID_result.xlsx", index=False)

    browser.quit()

    return path
