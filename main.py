from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import progressbar
import pandas as pd

options = Options()
options.add_argument("headless")
driver = webdriver.Edge(options=options)
driver.get('https://www.stonybrook.edu/sb/bulletin/current/courses/browse/byname/')

table = driver.find_element(By.ID, 'bulletin_course_search_table')
fields = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
field_urls = [field.find_element(By.TAG_NAME, 'td').find_element(By.TAG_NAME, 'a').get_attribute("href")  for field in fields]
result = []
bar = progressbar.ProgressBar(maxval=len(field_urls)).start()
for i,url in enumerate(field_urls,start=0):
    bar.update(i)
    driver.get(url)
    try:
        department = driver.find_element(By.CLASS_NAME, 'column_2_text').find_element(By.TAG_NAME,'h1').get_attribute('innerText')
        courses = driver.find_elements(By.CLASS_NAME, 'course')
        parsed_courses = []
        for course in courses:
            try:
                sbc = " ".join([s.get_attribute("innerText") for s in course.find_elements(By.TAG_NAME, 'span')[-1].find_element(By.XPATH, "..").find_elements(By.TAG_NAME, 'a')])

            except:
                sbc = "No fulfillments"
            prerequisite = course.find_elements(By.TAG_NAME, 'p')[1].get_attribute("innerText")
            if (len(prerequisite) == 0 or prerequisite[0] != "P"):
                prerequisite = "No prerequisite"
            parsed_courses.append({
                "department": department,
                "id": department[:3] + " " + course.get_attribute("id"),
                "name": course.find_element(By.TAG_NAME, 'h3').get_attribute("innerText").split(":")[1],
                "prerequisite": prerequisite,
                "SBC": sbc,
                "credits": course.find_elements(By.TAG_NAME, 'p')[-1].get_attribute("innerText")[0]
            })
        result += parsed_courses
    except:
        pass
bar.finish()
driver.quit()
df = pd.DataFrame(result)
df.to_csv("./courses.csv",index = False)
