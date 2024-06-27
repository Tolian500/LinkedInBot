from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from tags import tags
import time
import os
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

email = os.environ["EMAIL"]
password = os.environ["PASSWORD"]

print(email, password)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("incognito")
chrome_options.add_argument("--lang=en")
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)


def reload_page():
    driver.get(
        "https://www.linkedin.com/jobs/search/?currentJobId=3955959954&f_LF=f_AL&geoId=105076658&keywords=software%20developer&location=Warsaw%2C%20Mazowieckie%2C%20Poland&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true")


def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


def can_scroll_down(driver):
    # Get the current scroll position and the total scroll height
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    total_scroll_height = driver.execute_script("return document.body.scrollHeight;")
    view_port_height = driver.execute_script("return window.innerHeight;")

    # Check if we can scroll further
    return current_scroll_position + view_port_height < total_scroll_height


def get_all_offers():
    # Find all 'li' elements under the specified XPath
    # elements = driver.find_elements(By.XPATH,
    #                                 "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/ul/li")
    # elements = driver.find_elements(By.XPATH, '/html/body/div[3]/div/main/section[2]/ul/li')
    elements = driver.find_elements(By.CSS_SELECTOR, 'li.jobs-search-results__list-item')

    # Extract text content from each 'li' element and store in a list
    element_list = [element for element in elements]

    # Print the list
    print(element_list)
    print(len(element_list))
    return elements


def scroll_to_the_end():
    while can_scroll_down(driver):
        try:
            # reload_button = driver.find_element(By.LINK_TEXT, value="Дивитися більше вакансій")
            # Locate the button using aria-label (Note: Not all versions of Selenium support By.ariaLabel)
            reload_button = driver.find_element(By.CSS_SELECTOR,
                                                "button.infinite-scroller__show-more-button--visible[aria-label='Дивитися більше вакансій']")
            reload_button.click()
            print(f"Button was clicked: {reload_button}")
            time.sleep(0.2)
            scroll_down()
        except:
            scroll_down()
            time.sleep(0.2)
            print("Button not found, scrolling down")
    print("End of the page")


def login():
    sign_button = driver.find_element(By.LINK_TEXT, value="Sign in")
    sign_button.click()
    time.sleep(3)
    element = driver.find_element(By.ID, "username")
    element.send_keys(email)
    time.sleep(1)
    element = driver.find_element(By.ID, "password")
    element.send_keys(password, Keys.ENTER)
    time.sleep(6)


def collect_main_data():
    # Initialize an empty dictionary to store job offer details
    job_offer = {}

    # Extract company name
    company_name_element = driver.find_element(By.CLASS_NAME, 'job-details-jobs-unified-top-card__company-name')
    job_offer['Company Name'] = company_name_element.text.strip() if company_name_element else None

    # Extract job title
    job_title_element = driver.find_element(By.CLASS_NAME, 'job-details-jobs-unified-top-card__job-title')
    job_offer['Job Title'] = job_title_element.text.strip() if job_title_element else None

    # Extract employment type and experience level
    job_insight_elements = driver.find_elements(By.CLASS_NAME,
                                                'job-details-jobs-unified-top-card__job-insight-view-model-secondary')
    if len(job_insight_elements) >= 2:
        job_offer['Employment Type'] = job_insight_elements[0].text.strip()
        job_offer['Experience Level'] = job_insight_elements[1].text.strip()

    # Extract when posted and applicants
    description_element = driver.find_element(By.CLASS_NAME,
                                              'job-details-jobs-unified-top-card__primary-description-container')
    if description_element:
        description_texts = description_element.text.strip().split('·')
        if len(description_texts) >= 2:
            job_offer['Posted'] = description_texts[1].strip()
        if len(description_texts) >= 3:
            job_offer['Applicants'] = description_texts[2].strip()

    # Print the extracted job offer dictionary
    # print(job_offer)
    return job_offer


def search_tags_and_update_job_offer(driver, job_offer, search_tags):
    # List of tags to search for in the job description
    # search_tags = ['Python', 'Selenium', 'Git', 'Web crawling', 'Web scraping']

    # Initialize tag indicators to 0 (not found)
    for tag in search_tags:
        job_offer[tag] = 0

    # Find the job description element
    job_description_element = driver.find_element(By.ID, 'job-details')

    # Check if each tag is present in the job description
    for tag in search_tags:
        if tag in job_description_element.text:
            job_offer[tag] = 1
    print(job_offer)


def try_focus():
    try:
        # Find the element by ID
        element = driver.find_element(By.XPATH,
                                      "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div/div[4]")

        # Example: Scroll to the element using ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        # Example: Focus on the element (click it, if necessary)
        element.click()

        # You can perform other actions as needed, such as retrieving text or attributes

    finally:
        pass
        # # Close the WebDriver session
        # driver.quit()


def try_zoom():
    try:
        # Simulate pressing CTRL and '-' keys to zoom out
        webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys(Keys.SUBTRACT).key_up(Keys.CONTROL).perform()
    except:
        print("Zoom not possible")


# Function to save HTML after login
def save_html_after_login():
    page_source = driver.page_source
    with open('linkedin_jobs_page.html', 'w', encoding='utf-8') as f:
        f.write(page_source)


# Function to parse HTML with BeautifulSoup
def parse_html_with_bs():
    with open('linkedin_jobs_page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Example: Extract job titles
    job_titles = soup.find_all('a', class_='job-card-container__link job-card-list__title')

    for title in job_titles:
        print(title.text.strip())


# Function to generate unique filename
def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"job_offers_{timestamp}.json"


def save_file():
    # Save job offers list to JSON file
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(job_offers_list, json_file, ensure_ascii=False, indent=4)

    print(f"Job offers data saved to {output_filename}")


def change_page():
    global page
    pager = driver.find_element(By.ID, value="ember267")
    driver.execute_script("arguments[0].scrollIntoView(true);", pager)
    next_page_str = str(page + 1)
    time.sleep(0.5)
    next_page_str = f"Page {next_page_str}"
    # Find the button element using XPath
    next_page_button = driver.find_element(By.XPATH, f"//button[@aria-label='{next_page_str}']")
    next_page_button.click()
    page += 1


def unlock_all_offers():
    # Get all offers
    offers = get_all_offers()
    offer_number = len(offers)

    # Load all page first:
    for offer in offers:
        driver.execute_script("arguments[0].scrollIntoView(true);", offer)
        offer.click()
        time.sleep(1)
    return offers


def get_all_data(offers):
    # Loop to iterate over each offer
    for offer in offers:
        try:
            # # Get fresh list of offers
            # offers = get_all_offers()

            # Click on the x-th offer
            offer.click()

            # Collect main data from the offer
            data = collect_main_data()

            # Process the collected data (example: searching tags)
            if data:
                search_tags_and_update_job_offer(driver, data, tags)
                job_offers_list.append(data)  # Append the job offer dictionary to the list
                time.sleep(1)
                save_file()
            else:
                print("Failed to collect data for the job offer.")
                continue

        except StaleElementReferenceException as e:
            print(f"StaleElementReferenceException occurred: {str(e)}")
            continue

        except NoSuchElementException as e:
            print(f"NoSuchElementException occurred: {str(e)}")
            continue

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            continue

        finally:
            pass


# Initialize an empty list to store job offers
job_offers_list = []

# Enter Sign In page
reload_page()
time.sleep(2)
login()
time.sleep(8)
page = 1
one_more_page = True
# Generate a unique filename
output_filename = generate_filename()

# FOR EVERY PAGE:
while one_more_page is True:
    offers = unlock_all_offers()
    get_all_data(offers)
    time.sleep(3)
    # CHANGE PAGE:
    try:
        change_page()
        time.sleep(5)
    except:
        print("This is the last page")
        one_more_page = False



# Navigate back to the job search results page after each iteration
# driver.back()


# for x in range(offer_number):
#     offers = get_all_offers()
#     try:
#         offers[x].click()
#         data = collect_main_data()
#         if data:
#             search_tags_and_update_job_offer(driver, data, tags)
#             time.sleep(1)
#         else:
#             print("Failed to collect data for the job offer.")
#             continue
#     except StaleElementReferenceException as e:
#         print(f"StaleElementReferenceException occurred: {str(e)}")
#         continue
#     except Exception as e:
#         print(f"Exception occurred: {str(e)}")
#         continue
#     finally:
#         pass
#         # driver.back()  # Navigate back to the job search results page


# job_title = driver.find_element(By.CLASS_NAME, 'description__job-title').text.strip()
# company_name = driver.find_element(By.CLASS_NAME, 'description__company-name').text.strip()


# Extract seniority level if available
# seniority_level = None
# try:
#     seniority_level = driver.find_element(By.XPATH,
#                                           './/li[contains(@class, "description__job-criteria-item")]//h3[contains(@class, "description__job-criteria-subheader")]//following-sibling::span[contains(@class, "description__job-criteria-text")]').text.strip()
# except NoSuchElementException:
#     pass
#
# print(seniority_level)
# driver.back()
# offers[12].click()
# seniority_level = None
# try:
#     seniority_level = driver.find_element(By.XPATH,
#                                           './/li[contains(@class, "description__job-criteria-item")]//h3[contains(@class, "description__job-criteria-subheader")]//following-sibling::span[contains(@class, "description__job-criteria-text")]').text.strip()
# except NoSuchElementException:
#     pass
#
# print(seniority_level)
# # reload_button = None
#
#


# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# # application_list = driver.find_elements(By.CLASS_NAME, value="ember-view")


# application_list = driver.find_elements(By.CSS_SELECTOR, value=".scaffold-layout__list-container li a")
# print(len(application_list))
#
# for application in application_list:
#     print(application.text)
#     application.click()
#     time.sleep(1)
#     save_button = driver.find_element(By.CLASS_NAME, value="jobs-save-button")
#     save_button.click()
#     time.sleep(1)

#
# driver.close()
#
# driver.quit()

# Searching items by selenium:
# from selenium.webdriver.common.by import By
#
# Find element by name:
# driver.find_element(By.NAME, value="")
#
# Find element by class name
# driver.find_element(By.CLASS_NAME, value="")
#
# Find element by ID
# driver.find_element(By.ID, value="")
#
# Find element by CSS parent object part of a  class
# Example:
# driver.find_element(By.CSS_SELECTOR, value=".documentation-widget")
#
# IMPORTANT: need to use CSS symbols (#, . )
# If looking for ID = 		#idname
# If looking for class = 	.classname
# Click on object:
# all_portals.click()
#
# Find clickable object by text value
# all_portals = driver.find_element(By.LINK_TEXT, value= "Увійти")
#
# # Sending a key to input
# search.send_keys("Python")
#
# # Sending a specific key or buttons  to input
# from selenium.webdriver.common.keys import Keys
# search.send_keys("Python",Keys.ENTER)
