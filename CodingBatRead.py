import csv
import glob
import os
import sys
import getpass
from datetime import date

import requests
from bs4 import BeautifulSoup

'''
This program was written for Python 3

MIT License

Copyright (c) 2020 Thomas Kiesel <thomas.j.kiesel@gmail.com>
With modifications by Evan Sayles <evan.sayles@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# --------- User edits begin here ------------

# Login Credentials (leave blank to be prompted on program start)
username = ''
password = ''

# Should the program print the names of students who haven't
# finished any problems since the last grade pull?
printNone = True

# --------- End of User edits ----------------

if username == '':
    username = input("CodingBat email: ")
if password == '':
    password = getpass.getpass("Password: ")

# CodingBat post fields
userfield = 'uname'
passwdfield = 'pw'

# CodingBat urls
login_url = 'https://codingbat.com/login'
fetch_url = 'https://codingbat.com/report'

# today's date
today = date.today().strftime("%Y-%m-%d")

# filename prefix and suffix
prefix = 'codingbat_scores_'
suffix = '.csv'

# filename
csvfile = prefix + today + suffix

# filename search string for glob
searchstring = os.getcwd() + os.path.sep + prefix + '*' + suffix

# make session
session = requests.Session()

# Credentials
credentials = {userfield: username, passwdfield: password}

# Post credentials
session.post(login_url, data=credentials)

# Load the CodingBat report page.
reportpage = session.get(fetch_url)

# Parse the report page with BeautifulSoup
soup = BeautifulSoup(reportpage.text, 'html.parser')

with open(csvfile, 'w', newline='') as file:

    writer = csv.writer(file)

    # Section names
    sections = []
    sections.append('User ID')
    sections.append('Memo')
    sectionkeys = soup.find_all(attrs={"name": "sectionkey"})
    for key in sectionkeys:
        sections.append(key.attrs.get('value'))
    sections.append('Total')
    writer.writerow(sections)

    i = 0
    trs = soup.find_all('tr')
    for tableTR in trs:
        if i >= 5:
            student = []
            tds = tableTR.find_all('td')
            j = 0
            for tableTD in tds:
                if j == 0 or j == 1:
                    student.append(str(tableTD.text))
                else:
                    student.append(int(float(str(tableTD.text).strip() or 0)))
                j = j + 1
            writer.writerow(student)
        i = i + 1

# Get the list of all CodingBat csv files, sort by newest.
filelist = glob.glob(searchstring)
filelist.sort(reverse=True)

# Terminate if only one csv file has been created yet.
if len(filelist) < 2:
    print("First set of CodingBat scores have been read and stored in " + csvfile + " ... Exiting.")
    sys.exit()


def get_students(filename):
    students = []
    with open(filename, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            students.append(row)
    return students


filenew = get_students(filelist[0])[1:]  # skip the column titles
fileold = get_students(filelist[1])[1:]
sections = get_students(filelist[0])[0]
filenew_names = [s[0] for s in filenew]
fileold_names = [s[0] for s in fileold]

print("Generating changes since \"" + filelist[1] + "\"\n")

# check for removed students
for oldname in fileold_names:
    if not (oldname in filenew_names):
        print(oldname + " has been removed from your report since the last score pull.\n")

# check for added students
for newname in filenew_names:
    if not (newname in fileold_names):
        print(newname + " has been added to your report since the last score pull.\n")


for student in filenew:
    printed = False
    student_name = student[0]
    student_memo = student[1]
    for i in range(2, len(student)):  # skip the name and memo columns
        # check to see if this student appears in the last report
        if student_name in fileold_names:
            old_idx = fileold_names.index(student_name)
            newVal = int(student[i])
            oldVal = int(fileold[old_idx][i])
            if newVal > oldVal:
                print(student_memo + " <" + student_name + ">" + " has done " + str(newVal - oldVal) +
                      " more problems in section " + sections[i])
                printed = True
        else:
            printed = False
    if printed:
        print()
    elif printNone:
        print(student[1] + " <" + student_name + "> hasn't done any problems since the last score pull.\n")

