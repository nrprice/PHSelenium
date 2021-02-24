import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import json
import os
import pandas as pd
cwd = os.getcwd()
# Allows easy option to display / hide the browser window
display_brower_window = False
if display_brower_window == False:
    opts = Options()
    opts.headless = True
    assert opts.headless
    browser = Chrome(f'{cwd}/chromedriver', options=opts)

else:
    browser = Chrome(f'{cwd}/chromedriver')

URL = 'https://www.pearsonham.com/'
# Navigates to the URL
browser.get(URL)
time.sleep(0.5)
# Finds and clicks hamburger menu to open menu
browser.find_element_by_id('hamburger').click()
time.sleep(0.1)
# Finds and clicks the team link via the xpath
browser.find_element_by_xpath('//*[@id="menu-item-52"]/a').click()

# Instantiate empty employee dictionary
employee_dict = {}
id_num = 1
# Finds information about each individual team member
team_detail = browser.find_elements_by_class_name('team_detail')


for team_member in team_detail:

    if id_num in employee_dict.keys():
        print('Duplicate id_num')
        exit()

    # Retrieve team member name and qualification
    details = team_member.find_element_by_tag_name('h3').get_attribute('innerText').split(',')
    name = details[0].title()
    # Handles edge case where a team member does not have a qualification named.
    if len (details) > 1:
        qualification = details[1].strip()
    else:
        qualification = 'None Found'

    # Retrieve team member bio
    bio = team_member.find_element_by_class_name('team_memember_bio_copy').get_attribute('innerText').lstrip()
    bio = bio.replace('\t', ' ')

    # Retrieve team member background/education information
    background_class = team_member.find_element_by_class_name('background').get_attribute('textContent').split('\t')

    # This could be made better. Shouldn't be one line.
    # Quick fix to handle the wide variations in incoming data format.
    background_class = [x.replace('\x0b', '\n').strip() for x in background_class if len(x) != 0 and x != '\n' and x != 'BACKGROUND\n' and x != 'EDUCATION\n']

    # Handles edge case where no information is present
    if len(background_class) > 0:
        background = background_class[0].split('\n')
        education = background_class[1].split('\n')
    else:
        background = ['None Found']
        education = ['None Found']

    # Handles edge cases where incoming data was not formatted the same
    # Makes a best attempt to ascertain information regardless
    try:
        university = education[1]

        # Initially tried the same idea with finding the subject studied.
        # This currently does not work due to the differing formats of the data.

        # subject = education[0]
    except IndexError:
        university = education[0]
        # subject = 'None Found'

    # Handles edge case where universities where entered alongside the qualifcation obtained
    university = university.split(',')[-1].title()
    for r in (
              ('Beng', ''),
              ('Msc', ''),
              ('Bsc', ''),
              ('Mba', ''),
              ('(', ''),
              (')', '')
    ):
        university = university.replace(*r).strip()
        # subject = subject.replace(*r).strip()

    # Appends each employee and their information
    employee_dict.update({id_num:
                              {'name': name,
                               'qualification': qualification,
                               'biography': bio,
                               'background': background,
                               'prior_companies_worked': len(background),
                               'full_education': education,
                               'first_university': university,}
                          })
    # Inrements to ensure ID num is always unique
    id_num += 1

browser.quit()

save_JSON = True
if save_JSON:
    # Save scraped information to JSON
    with open ('pearsonham.txt', 'w') as file:
        json.dump(employee_dict, file)

"""
The JSON file can easily be read by pandas by specifying orient='index' with pd.read_json()
"""
