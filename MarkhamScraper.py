import csv
import sys
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from os import path

nstoppos = -1
desturl = "https://www.markham.ca/wps/portal/home/business/building-permits/eplan/public-search-and-sign-on"
destiframeurl = "https://opal.markham.ca/Markham/sfjsp"

dir_path = os.path.dirname(os.path.realpath(__file__))
#start scrapping

browser = webdriver.Chrome(dir_path + '/chromedriver')
browser.get(desturl)

time.sleep(3)
#reconnect iframe url
browser.get(destiframeurl)

#find search button and click
browser.find_element_by_xpath('''//*[@id="div_d_1482930323468"]/button''').click()
#find select combo
streetsele = browser.find_element_by_id("d_1479459348233")
streetcount = 0
streetarray = []

for option in streetsele.find_elements_by_tag_name('option'):
    streetcount += 1
    streetarray.append(option.text.strip())


timestr = time.strftime("%Y%m%d-%H%M%S")
storefile = dir_path + "/Markham"+timestr+".csv"
stopposfile = dir_path + "/MarkhamStreetpos.txt"

#for option in select_street.find_elements_by_tag_name('option'):
#    if option.text == value:
#        break

storf=open(storefile, 'a+')
#headers='Street Name,Street Type,Application Number,Address,Description,Status,Date \n'
#storf.write(headers)
storf.close()


isstopfile =  path.exists(stopposfile)
if isstopfile == True:
    filepos = open(stopposfile, "r")
    line = filepos.readline()
    filepos.close()
    nstoppos = int(line)
else:
    nstoppos = -1


i=1
while i < streetcount:

    if nstoppos != -1:
        if i < nstoppos:
            i = i + 1
            continue


    filepos = open(stopposfile, "w+")
    filepos.write('{}'.format(i))
    filepos.close()


    if storf.closed == True:
        storf = open(storefile, 'a+')

    select_street = Select(browser.find_element_by_id("d_1479459348233"))
    select_street.select_by_index(i)

    time.sleep(8)

    typerray = []

    try:
        select_typeele = browser.find_element_by_id("d_1479459348232")
        select_typecount = 0

        for option in select_typeele.find_elements_by_tag_name('option'):
            select_typecount += 1
            typerray.append(option.text.strip())


    except NoSuchElementException:
        print("can not find type element\n")
        continue

    print("scrape start {0}  : {1}  :type {2} \n".format(i, streetarray[i], select_typecount))
    j = 0
    while j < select_typecount:

        select_street = Select(browser.find_element_by_id("d_1479459348233"))
        select_street.select_by_index(i)

        time.sleep(2)

        try:
            eletype = browser.find_element_by_id("d_1479459348232")
            tmp_typecount = 0
            for option in eletype.find_elements_by_tag_name('option'):
                tmp_typecount += 1

            #select_type = Select(browser.find_element_by_id("d_1479459348232"))
            select_type = Select(eletype)
            select_type.select_by_index(j)

            browser.find_element_by_xpath('''//*[@id="div_d_1479459348234"]/button''').click()

            #write someting
            time.sleep(1)
        except NoSuchElementException:
            print("can not find type element\n")
            time.sleep(3)
            continue

        allselectXpath = ''
        allselectBody = ''

        try:
            hedev = browser.find_element_by_xpath('''//*[@id="div_d_1489057115756"]/div[2]''')
            #div_names = hedev.find_element_by_class_name("dataTables_wrapper form-inline dt-bootstrap no-footer")
            #div_names = hedev.find_element_by_css_selector("#DataTables_Table*")
            div_names = hedev.find_element_by_xpath('''.//div[@class='dataTables_wrapper form-inline dt-bootstrap no-footer']''')

            strpattern =  div_names.get_attribute("id")
            strpattern = strpattern[:-8]
            #strpattern = div_names.get_property("id")

            allselectXpath = '''//*[@id="''' + strpattern + '''_length"]/label/select'''
            allselectBody = '''//*[@id="''' + strpattern + '''"]/tbody'''

            #detailele = browser.find_element_by_xpath('''//*[@id="div_d_1489057115756"]/div[2]''')

            detailselect = Select(browser.find_element_by_xpath(allselectXpath))
            detailselect.select_by_index(3)
            time.sleep(1)

            tag_names = browser.find_element_by_xpath(allselectBody).find_elements_by_tag_name("tr")
            for tag in tag_names:
                tds = tag.find_elements_by_tag_name("td")

                linestr = streetarray[i] + "\t"
                linestr += typerray[j]

                tdcount = 0
                for tdtxt in tds:
                    if tdcount != 0:
                        linestr += ("\t" + tdtxt.text.strip())
                    tdcount += 1


                linestr += '\n'
                print(linestr)
                storf.write(linestr)
            #tag_names = browser.find_element_by_xpath(allselectBody).find_elements_by_tag_name("tr")

        except NoSuchElementException:
            print("can not find  developing element\n")

        time.sleep(1)
        # back search page
        try:
            browser.find_element_by_xpath('''//*[@id="div_d_1479459348405"]/button''').click()
        except NoSuchElementException:
            browser.execute_script("window.history.go(-1)")

        j += 1

    i += 1
    storf.close()

print("scrapping finish")


