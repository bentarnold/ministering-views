# MIT License
#
# Copyright (c) 2020 Ben Arnold
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
from html.parser import HTMLParser
import pprint
from datetime import datetime, date
import os

VERBOSE = True

pp = pprint.PrettyPrinter()

if not os.path.exists('reports'):
  os.makedirs('reports')


# -------------------------------------------------------------------
# Member Directory
# https://lcr.churchofjesuschrist.org/services/umlu/report/member-list?lang=eng&unitNumber=[your_unit_number_here!]

if VERBOSE:
  print('Parsing member list json data...')
  
with open("member-list.json") as directory_file:
  members = json.load(directory_file)

members_eq = []
members_rs = []
households = {}

for member in members:
  if member['householdRole'] == 'OTHER':
    continue

  if member['sex'] == 'M':
    members_eq.append(member)
  if member['sex'] == 'F':
    members_rs.append(member)
  
  household = member['householdMember']['household']
  uuid = household['anchorPerson']['uuid']
  if uuid in households:
    households[uuid].append(member)
  else:
    households[uuid] = [member]

if VERBOSE:
  print('Done.')

if VERBOSE:
  print('')


# -------------------------------------------------------------------
# Define the HTML parser

class MyHTMLParser(HTMLParser):
  def __init__(self):
    self.start_str = '<script id="__NEXT_DATA__"'
    self.ministering_data = {}
    super().__init__()

  def handle_data(self, data):
    if self.get_starttag_text() is not None and \
      self.start_str in self.get_starttag_text():
      self.ministering_data = data


# -------------------------------------------------------------------
# Ministering Assignments (EQ)
# https://lcr.churchofjesuschrist.org/ministering?lang=eng&type=EQ

if VERBOSE:
  print('Parsing EQ HTML/json data...')

with open("Ministering Brothers.html") as html_file:
  parser = MyHTMLParser()
  html_data = html_file.read()
  parser.feed(html_data)
  
  objs = json.loads(parser.ministering_data)
  data_eq = objs['props']['pageProps']['initialState']['ministeringData']['elders']
  companionships_eq = data_eq[0]['companionships']

if VERBOSE:
  print('Done.\n')


# -------------------------------------------------------------------
# Ministering Assignments (RS)
# https://lcr.churchofjesuschrist.org/ministering?lang=eng&type=RS

if VERBOSE:
  print('Parsing RS HTML/json data...')

with open("Ministering Sisters.html") as html_file:
  parser = MyHTMLParser()
  html_data = html_file.read()
  parser.feed(html_data)
  
  objs = json.loads(parser.ministering_data)
  data_rs = objs['props']['pageProps']['initialState']['ministeringData']['reliefSociety']
  companionships_rs = data_rs[0]['companionships']

if VERBOSE:
  print('Done.\n')


# -------------------------------------------------------------------
# Process data

root_dir = 'reports/'
assignments_file = 'ministering-assignments.csv'
stats_eq_file = 'ministering-stats-EQ.csv'
stats_rs_file = 'ministering-stats-RS.csv'

companionships_eq_by_id = {}
companionships_rs_by_id = {}
companionships_all = {}

assignments_eq_by_id = {}
assignments_rs_by_id = {}

# ------------------------------------------
# find ministers associated with each EQ
# member and save with key 'personUuid'

for companionship in companionships_eq:
  if 'assignments' not in companionship:
    print('Missing household in assignment:')
    pp.pprint(companionship)
    continue
  recipient_id = companionship['assignments'][0]['personUuid']
  if 'ministers' in companionship:
    ministers = companionship['ministers']
    companionships_eq_by_id[recipient_id] = ministers

for companionship in companionships_eq:
  ministers = companionship['ministers']
  if 'assignments' in companionship:
    recipients = companionship['assignments']
  else:
    recipients = []
  for recipient in recipients:
    for minister in ministers:
      minister_id = minister['personUuid']
      if minister_id in assignments_eq_by_id:
        assignments_eq_by_id[minister_id].append(recipient)
      else:
        assignments_eq_by_id[minister_id] = [recipient]

for companionship in companionships_rs:
  if 'assignments' not in companionship:
    print('Missing household in assignment:')
    pp.pprint(companionship)
    continue
  recipient_id = companionship['assignments'][0]['personUuid']
  if 'ministers' in companionship:
    ministers = companionship['ministers']
    companionships_rs_by_id[recipient_id] = ministers
    
for companionship in companionships_rs:
  ministers = companionship['ministers']
  if 'assignments' in companionship:
    recipients = companionship['assignments']
  else:
    recipients = []
  for recipient in recipients:
    for minister in ministers:
      minister_id = minister['personUuid']
      if minister_id in assignments_rs_by_id:
        assignments_rs_by_id[minister_id].append(recipient)
      else:
        assignments_rs_by_id[minister_id] = [recipient]

for uuid in households:
  ministers_eq = []
  ministers_rs = []
  for member in households[uuid]:
    if member['uuid'] in companionships_eq_by_id:
      for minister in companionships_eq_by_id[member['uuid']]:
        ministers_eq.append(minister)
    if member['uuid'] in companionships_rs_by_id:
      for minister in companionships_rs_by_id[member['uuid']]:
        ministers_rs.append(minister)
  companionships_all[uuid] = [ministers_eq, ministers_rs]

print('\n')
print('Writing assignments to file...')

with open(root_dir + assignments_file, 'w+') as f:
  f.write(('"Household","Brother 1","Sister 1",'
           '"Brother 2","Sister 2",'
           '"Brother 3","Sister 3",'
           '"Num Brothers","Num Sisters"\n'))
  for uuid in households:
    name = households[uuid][0]['householdNameDirectoryLocal']
    f.write('"%s"' % name)
    ministers_eq = companionships_all[uuid][0]
    ministers_rs = companionships_all[uuid][1]
    for idx in range(3):
      if idx < len(ministers_eq):
        f.write(',"%s"' % ministers_eq[idx]['name'])
      else:
        f.write(',')
      if idx < len(ministers_rs):
        f.write(',"%s"' % ministers_rs[idx]['name'])
      else:
        f.write(',')
    f.write(',%d,%d' % (len(ministers_eq), len(ministers_rs)))
    f.write('\n')

print('Done.\n')

print('Writing stats to file...')

def interviews_complete(minister):
  # convert interviews to datetime objects
  if 'interviews' not in minister:
    return [False, False, 'Never']
  interviews = []
  for interview in minister['interviews']:
    interviews.append(datetime.strptime(
      interview['date'][:10], '%Y-%m-%d'))
  
  # determine current and last quarters
  today = datetime.now()
  quarter_month = ((today.month - 1) // 3) * 3 + 1
  quarter_start = datetime(today.year, quarter_month, 1)
  if quarter_month == 1:
    prev_quarter_start = datetime(today.year-1, 10, 1)
  else:
    prev_quarter_start = datetime(today.year, quarter_month-3, 1)
  
  # determine status of interviews in
  # last two quarters
  last_interview = False
  prev_interview = False

  for interview in interviews:
    if interview >= quarter_start:
      last_interview = True
    if prev_quarter_start <= interview and \
       interview < quarter_start:
      prev_interview = True
  
  return [last_interview, prev_interview, interviews[-1]]

with open(root_dir + stats_eq_file, 'w+') as f:
  f.write('"Minister","Family 1","Family 2","Family 3","Family 4","Family 5","Count","Interviewed this quarter","Interviewed last quarter","Last Interview"\n')
  for member in members_eq:
    f.write('"%s",' % member['nameListPreferredLocal'])
    member_id = member['uuid']
    
    interviewed = [False, False, 'Never']
    for companionship in companionships_eq:
      for minister in companionship['ministers']:
        if member_id == minister['personUuid']:
          interviewed = interviews_complete(minister)
    date_last_interview = '%s' % interviewed[2]
    
    if member_id not in assignments_eq_by_id:
      f.write(',,,,,0,')
      f.write('%r,%r,%s\n' % (interviewed[0], interviewed[1], date_last_interview[:7]))
      continue
    for ii in range(5):
      assignment_count = len(assignments_eq_by_id[member_id])
      if ii < assignment_count:
        recipient = assignments_eq_by_id[member_id][ii]
        f.write('"%s",' % recipient['name'])
      else:
        f.write(',')
    f.write('%d,' % assignment_count)
    f.write('%r,%r,%s\n' % (interviewed[0], interviewed[1], date_last_interview[:7]))

with open(root_dir + stats_rs_file, 'w+') as f:
  f.write('"Minister","Family 1","Family 2","Family 3","Family 4","Family 5","Count","Interviewed this quarter","Interviewed last quarter","Last Interview"\n')
  for member in members_rs:
    f.write('"%s",' % member['nameListPreferredLocal'])
    member_id = member['uuid']
    
    interviewed = [False, False, 'Never']
    for companionship in companionships_rs:
      for minister in companionship['ministers']:
        if member_id == minister['personUuid']:
          interviewed = interviews_complete(minister)
    date_last_interview = '%s' % interviewed[2]
    
    if member_id not in assignments_rs_by_id:
      f.write(',,,,,0,')
      f.write('%r,%r,%s\n' % (interviewed[0], interviewed[1], date_last_interview[:7]))
      continue
    for ii in range(5):
      assignment_count = len(assignments_rs_by_id[member_id])
      if ii < assignment_count:
        recipient = assignments_rs_by_id[member_id][ii]
        f.write('"%s",' % recipient['name'])
      else:
        f.write(',')
    f.write('%d,' % assignment_count)
    f.write('%r,%r,%s\n' % (interviewed[0], interviewed[1], date_last_interview[:7]))

print('Done.')
