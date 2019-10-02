from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from collections import defaultdict
from selenium.webdriver.chrome.options import Options
from tkinter import messagebox
from tabulate import tabulate

import os
import time
import datetime
import re
import csv
import pandas as pd
import numpy as np


# Function Calls
def initiateChromeWebDriver():
    options = webdriver.ChromeOptions()
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        "download.default_directory": "/Users/ashokeerthi/Downloads/PythonDownLoadDirectory",
        "directory_upgrade": True,
        "safebrowsing.enabled": True,
        'profile': {
            'password_manager_enabled': False
        }
    })
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/Users/ashokeerthi/Downloads/PythonDownLoadDirectory ")

    chromeDriver = webdriver.Chrome("/Users/ashokeerthi/TechWorld/PythonProjects/PythonWorks/ChromeWebDriver/chromedriver", chrome_options=chrome_options)
    chromeHandle = chromeDriver.current_window_handle

    chromeDriver.maximize_window()

    return [chromeDriver, chromeHandle]

def getTheTeamStatistics(chromeDriver):

    teamDataDict = dict()
    dfTeamStatsConsolidate = pd.DataFrame()

    # Getting Team Details
    # Getting all Teams data
    chromeDriver.get('https://www.prokabaddi.com/stats/0-96-total-points-scored-statistics')
    time.sleep(10)

    # Get All Team details first
    # Click Each Team Name and Get the Details.
    teamsTable = "//li[@class = 'submenu    teams']/div[@class = 'submenu-item']/a"
    teamTable = chromeDriver.find_elements_by_xpath(teamsTable)

    for team in teamTable:
        teamDataDict[team.get_attribute('text')] = team.get_attribute('href')
        print(team.get_attribute('href'), "-->", team.get_attribute('text'))

    for teamName in teamDataDict.keys():
        print('Redirecting to ==> ', teamName)
        print('With URL ===>', teamDataDict[teamName])
        chromeDriver.get(teamDataDict[teamName])
        time.sleep(10)

        # Getting Seasons data
        seasons = '//div[@class="si-section-data si-right"]/div[@class="si-tbl-wraper si-tbl-header"]/div/div'
        seasons = [x.text for x in chromeDriver.find_elements_by_xpath(seasons)]

        # Getting Overall Data
        overallHeaders = '//div[@class="si-tbl-wraper si-overall"]/div[@class = "si-tbl-data"]/div'
        headers = chromeDriver.find_elements_by_xpath(overallHeaders)
        headers = [header.text for header in headers]
        headers.remove('HIGHEST SCORE')
        headers.remove('BIGGEST WINNING MARGIN')


        # Getting Attack Data
        attackData = '//div[@class="si-tbl-wraper si-attack"]/div[@class = "si-tbl-data"]/div'
        attacks = chromeDriver.find_elements_by_xpath(attackData)
        attacks = [attack.text for attack in attacks]

        # Getting Defence Data
        defenceData = '//div[@class="si-tbl-wraper si-defence"]/div[@class = "si-tbl-data"]/div'
        defences = chromeDriver.find_elements_by_xpath(defenceData)
        defences = [defence.text for defence in defences]

        # DataFrame rows
        indexi = list()
        indexi.append(headers)
        indexi.append(attacks)
        indexi.append(defences)
        indexi = [y for x in indexi for y in x ]

        # Look for Table Data Headers
        tableDataHeaders = '//div[@class="si-tbl-wraper"]/div[@class="si-tbl-data"]/div[@class="si-data-block"]'
        tableValues = [tableValue.text for tableValue in chromeDriver.find_elements_by_xpath(tableDataHeaders)]

        # for tableValue in chromeDriver.find_elements_by_xpath(tableDataHeaders):
        #     print(tableValue.text)

        # Construct the dataFrame with Rows and Columns
        df = pd.DataFrame(index=indexi, columns=seasons)

        # indexes need to consider
        overallEnd  = len(headers) * len(seasons)
        attackEnd   = len(headers) * len(seasons) + len(attacks) * len(df.columns)
        defenceEnd  = len(headers) * len(seasons) + len(attacks) * len(df.columns) + len(defences) * len(df.columns)

        overallStats = tableValues[0:overallEnd]
        attackStats = tableValues[overallEnd:attackEnd]
        defenceStats = tableValues[attackEnd:defenceEnd]

        df.loc[headers] = np.array(overallStats).reshape(-1, len(headers)).T
        df.loc[attacks] = np.array(attackStats).reshape(-1, len(attacks)).T
        df.loc[defences] = np.array(defenceStats).reshape(-1, len(defences)).T

        # Updating Team Name
        df['Team'] = teamName
        # dfTeamStatsConsolidate.append(df)
        dfTeamStatsConsolidate = pd.concat([dfTeamStatsConsolidate, df])
        print(df)
        print(">>===> "*5, "Updated Count", dfTeamStatsConsolidate.shape)

    return dfTeamStatsConsolidate

    # Team Data can be from
    # https://www.sportskeeda.com/go/pro-kabaddi/points-table

def getAllTeamPlayerStatistics(chromeDriver):
    teamDataDict = defaultdict()
    dfTeamPlayerStatistics = pd.DataFrame()

    chromeDriver.get('https://www.prokabaddi.com/stats/0-96-total-points-scored-statistics')
    time.sleep(10)

    # Click Team Data button
    teamButton = '//*[@id="team_Btn"]/span'
    teamButton = chromeDriver.find_element_by_xpath(teamButton)
    try:
        teamButton.click()
    except Exception as clickError:
        pass
    time.sleep(3)


    teamsTable = "//li[@class = 'submenu    teams']/div[@class = 'submenu-item']/a"
    teamTable = chromeDriver.find_elements_by_xpath(teamsTable)

    for team in teamTable:
        teamDataDict[team.get_attribute('text')] = team.get_attribute('href')
        print(team.get_attribute('href'), "-->", team.get_attribute('text'))

    for teamName in teamDataDict.keys():
        print('Redirecting to ==> ', teamName)
        print('With URL ===>', teamDataDict[teamName])
        chromeDriver.get(teamDataDict[teamName])
        time.sleep(10)

        # Click 'Full Squad" button to get list of individual players
        squadButton = "//span[text() = 'View Full Squad']"
        elem = chromeDriver.find_element_by_xpath(squadButton)
        elem.click()

        # All Players URL list
        playersDict = dict()
        playersList = '//div[@class="si-innerWrp"]/a'
        allPlayers = chromeDriver.find_elements_by_xpath(playersList)
        allPlayers = [x.get_attribute('href') for x in allPlayers]

        for player in allPlayers:
            playersDict[list(re.match(r'(.*?)-profile', player.split("/")[-1]).groups())[0]] = player

        for player in playersDict.keys():
            print("====== PROCESSING PLAYER *****{}***** STATS ======".format(player))
            print('*** WITH URL ***',playersDict[player])
            chromeDriver.get(playersDict[player])
            time.sleep(10)

            # Check for 'STATS' button and Click
            try:
                statsButton = '//div[@class="si-tab si-profile-tabs"]/span'
                statsButton = chromeDriver.find_element_by_xpath(statsButton)
                statsButton.click()
            except Exception as error:
                pass

            # Getting Seasons data
            seasons = '//div[@class="si-section-data si-right si-data-section"]/div[@class="si-tbl-wraper si-tbl-header"]/div/div'
            seasons = [x.text for x in chromeDriver.find_elements_by_xpath(seasons)]

            # Getting Overall Data
            overallHeaders = '//div[@class="si-tbl-wraper si-overall"]/div[@class = "si-tbl-data"]/div'
            headers = chromeDriver.find_elements_by_xpath(overallHeaders)
            headers = [header.text for header in headers]

            # Getting Attack Data
            attackData = '//div[@class="si-tbl-wraper si-attack"]/div[@class = "si-tbl-data"]/div'
            attacks = chromeDriver.find_elements_by_xpath(attackData)
            attacks = [attack.text for attack in attacks]

            # Getting Defence Data
            defenceData = '//div[@class="si-tbl-wraper si-defens"]/div[@class = "si-tbl-data"]/div'
            defences = chromeDriver.find_elements_by_xpath(defenceData)
            defences = [defence.text for defence in defences]

            # Look for Table Data Headers
            tableDataHeaders = '//div[@class="si-tbl-wraper"]/div[@class="si-tbl-data"]/div[@class="si-data-block"]'
            tableValues = [tableValue.text for tableValue in chromeDriver.find_elements_by_xpath(tableDataHeaders)]

            # DataFrame rows
            indexi = list()
            indexi.append(headers)
            indexi.append(attacks)
            indexi.append(defences)
            indexi = [y for x in indexi for y in x ]

            # Construct the dataFrame with Rows and Columns
            df = pd.DataFrame(index=indexi, columns=seasons)

            # indexes need to consider
            overallEnd  = len(headers) * len(seasons)
            attackEnd   = len(headers) * len(seasons) + len(attacks) * len(df.columns)
            defenceEnd  = len(headers) * len(seasons) + len(attacks) * len(df.columns) + len(defences) * len(df.columns)

            overallStats = tableValues[0:overallEnd]
            attackStats = tableValues[overallEnd:attackEnd]
            defenceStats = tableValues[attackEnd:defenceEnd]

            df.loc[headers] = np.array(overallStats).reshape(-1, len(headers)).T
            df.loc[attacks] = np.array(attackStats).reshape(-1, len(attacks)).T
            df.loc[defences] = np.array(defenceStats).reshape(-1, len(defences)).T

            # Updating Team Name
            df['Team']          = teamName
            df['Player Name']   = player
            # dfTeamStatsConsolidate.append(df)
            dfTeamPlayerStatistics = pd.concat([dfTeamPlayerStatistics, df])
            print(df)
            print(">>===> "*5, "Updated Count", dfTeamPlayerStatistics.shape)

    return dfTeamPlayerStatistics

def getThePointsTable(chromeDriver):
    dfTeamPoints = pd.DataFrame()
    chromeDriver.get('https://www.prokabaddi.com/standings')
    time.sleep(10)

    # Click The Drop Down and Select The Season
    # First Get the list of DropDowns
    # dropDownValues = '//select[@class="si-selectBox"]/option'
    # dropDownValues = chromeDriver.find_elements_by_xpath(dropDownValues)
    # dropDownValues = [x.get_attribute('text') for x in dropDownValues]

    for x in range(len(chromeDriver.find_elements_by_xpath('//span[contains(@data-name ,"season")]')), 0, -1):
        dropDownButton = '//div[@class="si-selectWrap si-web si-season-web"]'
        dropDownButton = chromeDriver.find_element_by_xpath(dropDownButton)
        # print(dropDownButton)
        print('Dropdown clicked....')
        dropDownButton.click()
        time.sleep(10)

        season = '//span[contains(@data-name ,"season {}")]'.format(x)
        seasonName = "season {}".format(x)

        print(season)
        seasonButton = chromeDriver.find_element_by_xpath(season)
        print('Dropdown before......')
        seasonButton.click()
        time.sleep(5)
        print('Season button clicked....', season)

        # Points Table Headers
        # headers = '//div[@class="sipk-zoneBlock-wrap"]/div/div//span[@class="si-fullName"]'
        # headers = [x.text for x in chromeDriver.find_elements_by_xpath(headers)]

        ranks = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-rank"]'
        ranks = [re.match(r'([0-9]+)', x.text).groups(0)[0] for x in chromeDriver.find_elements_by_xpath(ranks)]

        teams = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-team"]'
        teams = [x.text for x in chromeDriver.find_elements_by_xpath(teams)]

        playes = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-play"]'
        playes = [x.text for x in chromeDriver.find_elements_by_xpath(playes)]

        wons = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-won"]'
        wons = [x.text for x in chromeDriver.find_elements_by_xpath(wons)]

        losts = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-lost"]'
        losts = [x.text for x in chromeDriver.find_elements_by_xpath(losts)]

        draws = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-drow"]'
        draws = [x.text for x in chromeDriver.find_elements_by_xpath(draws)]

        scoreDiffs = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-scoreDiff"]'
        scoreDiffs = [x.text for x in chromeDriver.find_elements_by_xpath(scoreDiffs)]

        points = '//div[@class="standing-dataRow-wrap active"]/div[@class="sipk-table-col sipk-points"]'
        points = [x.text for x in chromeDriver.find_elements_by_xpath(points)]

        time.sleep(10)

        cols = ['Rank', 'Plays', 'Won', 'Lost', 'Draw', 'Score Diff', 'Points']

        df = pd.DataFrame(index = teams)
        df['Rank']  = ranks
        df['Plays'] = playes
        df['Won']   = wons
        df['Lost']  = losts
        df['Draw']  = draws
        df['scoreDiff'] = scoreDiffs
        df['Points']    = points
        df['Season'] = seasonName

        dfTeamPoints = pd.concat([dfTeamPoints, df])
        print(dfTeamPoints.shape)

    return dfTeamPoints





# MAIN
pd.set_option('display.max_columns', 500)
# Initiate ChromeDriver
chromeDriver, chromeHandle = initiateChromeWebDriver()

# Get the Team Statistics
dfTeamStatistics = getTheTeamStatistics(chromeDriver)
dfTeamStatistics.to_csv('/Users/ashokeerthi/TechWorld/PythonProjects/PythonWorks/Upgrad_ProKabaddiHackthon_Code/outputStats/teamConsolidatedReport.csv')

# Get Player Statistics
dfPlayerStats = getAllTeamPlayerStatistics(chromeDriver)
dfPlayerStats.to_csv('/Users/ashokeerthi/TechWorld/PythonProjects/PythonWorks/Upgrad_ProKabaddiHackthon_Code/outputStats/teamPlayerConsolidatedReport.csv')

# Get the Points stats
dfTeamPoints  = getThePointsTable(chromeDriver)
dfTeamPoints.to_csv('/Users/ashokeerthi/TechWorld/PythonProjects/PythonWorks/Upgrad_ProKabaddiHackthon_Code/outputStats/teamPointsStats.csv')
