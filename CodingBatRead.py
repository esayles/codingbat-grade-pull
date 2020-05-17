import csv
import glob
import os
import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

'''
This program was written for Python 3

MIT License

Copyright (c) 2020 Thomas Kiesel <thomas.j.kiesel@gmail.com>

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

## --------- User edits begin here ------------

# Login Credentials
username = ''
password = ''

# Should the program print the names of students who haven't
# finished any problems since the last grade pull?
printNone = True

## --------- End of User edits ----------------

# Codingbat post fields
userfield = 'uname'
passwdfield = 'pw'

# Codingbat urls
login_url = 'https://codingbat.com/login'
fetch_url = 'https://codingbat.com/report'

#today's date
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
credentials = {userfield:username, passwdfield:password}

# Post credentials
session.post(login_url, data=credentials)

# Load the CodingBat report page.
reportpage = session.get(fetch_url)

# Parse the report page with BeautifulSoup
soup = BeautifulSoup(reportpage.text, 'html.parser')

with open( csvfile, 'w', newline='') as file:

    writer = csv.writer(file)

    # Section names
    sections = []
    sections.append('User ID')
    sections.append('Memo')
    sectionkeys = soup.find_all(attrs={"name": "sectionkey"})
    for key in sectionkeys :
        sections.append(key.attrs.get('value'))
    sections.append('Total')
    writer.writerow(sections)

    i = 0
    trs = soup.find_all('tr')
    for tableTR in trs :
        if i >= 5 :
            student = []
            tds = tableTR.find_all('td')
            j = 0
            for tableTD in tds :
                if j == 0 or j == 1:
                    student.append( str(tableTD.text) )
                else :
                    student.append( int( float( str(tableTD.text).strip() or 0) ) )
                j = j + 1
            writer.writerow(student)
        i = i + 1

# Get the list of all codingbat csv files, sort by newest.
filelist = glob.glob( searchstring )
filelist.sort(reverse=True)

# Terminate if only one csv file has been created yet.
if len(filelist) < 2 :
    print("First set of CodingBat scores have been read and stored in " + csvfile + " ... Exiting.")
    sys.exit()

def getStudents( fileName ) :
    students = []
    with open(fileName, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            students.append(row)
    return students

fileold = getStudents( filelist[1] )
filenew = getStudents( filelist[0] )

print( "Generating changes since \"" + filelist[1] + "\"\n")

for n, student in enumerate(filenew) :
    if n > 0:
        for m, student2 in enumerate(fileold) :
            if m > 0 and student[0] == student2[0] :
                printed = False
                for i in range( len( student ) ) :
                    if i > 1 :
                        newVal = int(student[i])
                        oldVal = int(student2[i])
                        if newVal > oldVal :
                            print( student[1] + " <"+student[0]+">" + " has done " + str(newVal - oldVal) + " more problems in section " + filenew[0][i] )
                            printed = True
                if printed :
                    print()
                elif printNone :
                    print(student[1] + " <"+student[0]+"> hasn't done any problems since the last score pull.\n")