from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import pandas as pd
import time

options = Options()
options.add_argument("headless")
driver = webdriver.Edge(options=options)
driver.get('https://www.stonybrook.edu/sb/bulletin/current/courses/browse/byname/')

table = driver.find_element(By.ID, 'bulletin_course_search_table')
fields = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
field_urls = [field.find_element(By.TAG_NAME, 'td').find_element(By.TAG_NAME, 'a').get_attribute("href")  for field in fields]
result = []
for url in field_urls:
    driver.get(url)
    try:
        department = driver.find_element(By.CLASS_NAME, 'column_2_text').find_element(By.TAG_NAME,'h1').get_attribute('innerText')
        courses = driver.find_elements(By.CLASS_NAME, 'course')
        parsed_courses = []
        for course in courses:
            try:
                sbc = course.find_element(By.TAG_NAME, 'a').get_attribute("innerText")
            except:
                sbc = "No fulfillments"
            prerequisite = course.find_elements(By.TAG_NAME, 'p')[1].get_attribute("innerText")
            if (len(prerequisite) == 0 or prerequisite[0] != "P"):
                prerequisite = "No prerequisite"
            parsed_courses.append({
                "department": department,
                "name": department[:3] + " " + course.get_attribute("id") + ": " + course.find_element(By.TAG_NAME, 'h3').get_attribute("innerText").split(":")[1],
                "prerequisite": prerequisite,
                "SBC": sbc,
                "credits": course.find_elements(By.TAG_NAME, 'p')[-1].get_attribute("innerText")[0]
            })
        result += parsed_courses
    except:
        pass
driver.quit()
df = pd.DataFrame(result)
df.to_csv("./courses.csv")
