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
print("Step 1: Collecting Course Data ... ")
bar = progressbar.ProgressBar(maxval=len(field_urls)).start()
department_map = {}
for i,url in enumerate(field_urls,start=0):
    bar.update(i)
    driver.get(url)
    try:
        department = driver.find_element(By.CLASS_NAME, 'column_2_text').find_element(By.TAG_NAME,'h1').get_attribute('innerText').replace('"',"")
        courses = driver.find_elements(By.CLASS_NAME, 'course')
        parsed_courses = []
        for course in courses:
            try:
                sbc = " ".join([s.get_attribute("innerText") for s in course.find_elements(By.TAG_NAME, 'span')[-1].find_element(By.XPATH, "..").find_elements(By.TAG_NAME, 'a')])
            except:
                sbc = "None"
            prerequisite = course.find_elements(By.TAG_NAME, 'p')[1].get_attribute("innerText")
            if (len(prerequisite) == 0 or prerequisite[0] != "P"):
                prerequisite = "None"
            elif (":" in prerequisite):
                prerequisite = prerequisite.split(": ")[1]
            parsed_courses.append({
                "id": department[:3] + " " + course.get_attribute("id"),
                "name": course.find_element(By.TAG_NAME, 'h3').get_attribute("innerText").split(":")[1].replace('"',""),
                "prerequisite": prerequisite,
                "SBC": sbc,
                "credits": int(course.find_elements(By.TAG_NAME, 'p')[-1].get_attribute("innerText")[0])
            })
        department_map[department[:3]] = pd.DataFrame(parsed_courses)
    except:
        pass
bar.finish()
driver.quit()
print(department_map)
print("Step 2: Finding Optimal SBC Courses ... ")
print("Enter all of the required courses using comma as a separator. (Including WRT and SNW)")
print("Ex) >>> CSE 101, CSE 114, ... ,")
my_courses = input("Enter: ").split(", ")
fulfilled_sbc = []
required_sbc = set(["ARTS","GLO","HUM","LANG","QPS","SBS","SNW","TECH","USA","WRT","STAS","EXP+","HFA+","SBS+","STEM+","CER","DIV","ESI","SPK","WRTD"])
for course in my_courses:
    for _, row in department_map[course.split(" ")[0]]:
        print(row)
        for a in row:
            if a["id"] == course:
                fulfilled_sbc.append(a["SBC"])
required_sbc = list(required_sbc - set(fulfilled_sbc))

print("You need to take the following SBC courses: ", required_sbc)

# selected_courses = []
# for sbc in required_sbc:
#     for department in department_map:
#         max_course = (0,0,0)
#         for _, row in department:
#             if sbc in row["SBC"].split() and len(row["SBC"].split(" ")) > max[0]:
#                 max_course = (len(row["SBC"].split(" ")),row["id"],row["SBC"])
        