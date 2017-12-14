import csv
import datetime
import os


from selenium.common.exceptions import (NoSuchElementException)
from selenium import webdriver
from selenium.webdriver.support.ui import Select

BROWSER = webdriver.Firefox()
DATES_WITHOUT_DATA = []
FIELDNAMES = ['DATE', 'HOUR OF DAY ENDING AT L.S.T',
              'TOTAL SOLAR RAD (K W-hr/m^2)',
              'AVE WIND SPEED (m/s)', 'V. WIND DIR (Deg)',
              'MAX WIND SPEED (m/s)', 'AIR TEMP AVE (Deg C)',
              'AIR TEMP MAX (Deg C)', 'AIR TEMP MIN (Deg C)',
              'SOIL TEMP AVE (Deg C)', 'SOIL TEMP MAX (Deg C)',
              'SOIL TEMP MIN (Deg C)', 'RELATIVE HUMIDITY AVE (%)',
              'RELATIVE HUMIDITY MAX (%)', 'RELATIVE HUMIDITY MIN (%)',
              'DEW PT. (Deg C)', 'WET BULB (Deg C)', 'BARO. PRESS. (mb)',
              'SNOW DEPTH (mm)', 'TOTAL PRECIP (mm)']

# User Variables
start_year = 1997
start_month = "APR"
end_year = 2000
end_month = "DEC"
output_file_name = "sagehen_climate_data_{}{}-{}{}".format(start_month,
                                                           start_year,
                                                           end_month,
                                                           end_year)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def choose_date(datetime_obj):
    BROWSER.get("https://wrcc.dri.edu/cgi-bin/wea_daysum.pl?casagh")
    try:
        year_element = BROWSER.find_element_by_xpath(
                                                '/html/body/form/select[3]')
        year_select = Select(year_element)
        year_select.select_by_visible_text(str(datetime_obj.year))
    except NoSuchElementException:
        print("\nThe year specified does not exist within the dataset.\n")
        return False
    try:
        month_element = BROWSER.find_element_by_xpath(
                                                "/html/body/form/select[1]")
        month_select = Select(month_element)
        month_select.select_by_index(datetime_obj.month-1)
    except NoSuchElementException:
        print("\nThe month {} does not exist.\n".format(datetime_obj.month))
        return False
    try:
        day_element = BROWSER.find_element_by_xpath(
                                                "/html/body/form/select[2]")
        day_select = Select(day_element)
        day_select.select_by_index(datetime_obj.day-1)
    except NoSuchElementException:
        print("\n There is not a {} day in the {} month of {}.".format(
                                                day_num, month_num, year_num))
        return False

    metric_element = BROWSER.find_element_by_xpath(
                                        "/html/body/form/label[2]/input")
    metric_element.click()

    submit_button = BROWSER.find_element_by_xpath(
                                        "/html/body/form/input[3]")
    submit_button.click()


def grab_data(datetime_obj):
    try:
        center_element = BROWSER.find_element_by_xpath(
                                            "/html/body/center")
    except NoSuchElementException:
        bad_date = "{}-{}-{}".format(datetime_obj.year,
                                     datetime_obj.month,
                                     datetime_obj.day)
        DATES_WITHOUT_DATA.append(bad_date)
        print('NO DATA ON: {}'.format(bad_date))
        return False

    if "data not available" in center_element.text.lower():
        bad_date = "{}-{}-{}".format(datetime_obj.year,
                                     datetime_obj.month,
                                     datetime_obj.day)
        DATES_WITHOUT_DATA.append(bad_date)
        print('NO DATA ON: {}'.format(bad_date))
        return False
    
    data_table = []
    data_row = []

    rows = BROWSER.find_elements_by_class_name('data')
    for row in rows[:24]:
        nums = row.find_elements_by_tag_name('td')
        counter = 0
        data_row.append(datetime_obj.strftime("%Y-%m-%d"))
        for num in nums:
            num = num.text
            if counter == 0:
                hour, am_pm = num.split(' ')
                data_row.append(time_fix(int(hour), am_pm))
            elif counter in [1, 3, 4, 6, 8, 10, 11, 13, 15]:
                if num == '':
                    num = 'NAN'
                data_row.append(num)
            counter += 1
        data_table.append(data_row)
        write_data(data_row, FIELDNAMES)
        data_row = []
    return data_table


def time_fix(hour, am_pm):
    ''' Changes time from a 12 hour clock to a 24 hour clock. '''
    if am_pm == 'am':
        if hour in range(10):
            hour = '0{}'.format(hour)
        elif hour == 12:
            hour = '00'
    elif am_pm == 'pm':
        if hour != 12:
            hour = hour + 12
    return '{}:00'.format(hour)


def write_data(data_row, fieldnames):
    with open(output_file_name, 'a') as csv_file:
        hourlywriter = csv.DictWriter(csv_file, fieldnames=fieldnames)

        hourlywriter.writerow({
            'DATE': data_row[0],
            'HOUR OF DAY ENDING AT L.S.T': data_row[1],
            'TOTAL SOLAR RAD (K W-hr/m^2)': data_row[2],
            'AVE WIND SPEED (m/s)': data_row[3],
            'V. WIND DIR (Deg)': data_row[4],
            'MAX WIND SPEED (m/s)': 'NAN',
            'AIR TEMP AVE (Deg C)': data_row[5],
            'AIR TEMP MAX (Deg C)': 'NAN',
            'AIR TEMP MIN (Deg C)': 'NAN',
            'SOIL TEMP AVE (Deg C)': 'NAN',
            'SOIL TEMP MAX (Deg C)': 'NAN',
            'SOIL TEMP MIN (Deg C)': 'NAN',
            'RELATIVE HUMIDITY AVE (%)': data_row[6],
            'RELATIVE HUMIDITY MAX (%)': 'NAN',
            'RELATIVE HUMIDITY MIN (%)': 'NAN',
            'DEW PT. (Deg C)': data_row[7],
            'WET BULB (Deg C)': data_row[8],
            'BARO. PRESS. (mb)': data_row[9],
            'SNOW DEPTH (mm)': 'NAN',
            'TOTAL PRECIP (mm)': data_row[10],
        })


if __name__ == "__main__":
    clear()
    print('<<<<<<< Sagehen Climate Data Web Scraper >>>>>>>')
    for year in range(start_year, end_year + 1):
        print('YEAR: {}'.format(year))
        for month in range(1, 13):
            print('MONTH: {}'.format(month))
            for day in range(1, 32):
                if year == 1997 and month in [1, 2, 3, 11]:
                    pass
                elif year == 2000 and month >= 7:
                    pass
                else:
                    date = datetime.datetime(year, month, day)
                    choose_date(date)
                    if date:
                        grab_data(date)
    BROWSER.quit()
    os.system("say 'Sagehen Web Scraper Finished'")

    # # dates = [[1997, 4, 1], [1997, 4, 3], [2000, 7, 1], [2001, 9, 1],
    # #          [2001, 9, 19], [2002, 10, 1], [2002, 10, 3]]
    # dates = [[1997, 4, 1], [1997, 4, 3]]
    # for date_ints in dates:
    #     year_num, month_num, day_num = date_ints

    #     date = datetime.datetime(year_num, month_num, day_num)
    #     choose_date(date)
    #     clean_data = grab_data(date)
    #     for row in clean_data:
    #         print(row)
    #     print('')
    #     # input()
    BROWSER.quit()
