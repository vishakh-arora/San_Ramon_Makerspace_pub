import os
import random
from munkres import Munkres, print_matrix
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# reading google sheets data
# FOR MAKERSPACE UPDATE SPREADSHEET_ID AND CREDENTIALS FILE ONLY
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1JBGnKyjKqAYLGnDp-U0YU3ORfuCJ8AFZplH51NoiSTU'
RANGE = 'LockerTests!A2:D'

creds = None
if os.path.exists('token.json'):
  creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
  if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
  else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
  # Save the credentials for the next run
  with open('token.json', 'w') as token:
      token.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
result = sheet.values().get(
  spreadsheetId=SPREADSHEET_ID,
  range=RANGE).execute()
values = result.get('values', [])
values = [[i.strip() for i in j] for j in values]

x = {}
for i in values:
    x[i[0]] = i[1:]

name2num = {i:j for i,j in zip(x.keys(), range(len(x)))}
num2name = {j:i for i,j in name2num.items()}

for i in name2num.keys():
  for j in range(len(x[i])):
    x[i][j] = name2num[x[i][j]]
  x[name2num[i]] = x.pop(i)

# printing preferences
# (i, [a, b])
# a is i's first preference (weight 0)
# b is i's is second preference (weight 1)
# any other person (c, d, e, ...) has no preference and has weight 10
print('PREFERENCES:')
print(*x.items(), sep='\n')
print()

# turning preferences into a 2X2 matrix.
#
#   a b c d e f
# a x y z . . .
# b
# c
# d
# e
# f
#
# example 1:
# person a prefers b with weight 0 and b prefers a with weight 1.
# the corresponding m[a][b] = 0 + 1 = 1
#
# example 2:
# person a prefers b with weight 1, but does not prefer a.
# the corresponding m[a][b] = 1 + 10 = 11
# i chose 10 bc its a high number idk
#
# other notes:
# m[a][b] = m[b][a] always.
# to avoid algorithm partnering someone with themself
m = [[0 for i in range(len(x))] for i in range(len(x))]
for i in x.keys():
  for j in x.keys():
    cost = 0
    if j in x[i]:
      cost += x[i].index(j)
    else:
      cost += 10
    if i in x[j]:
      cost += x[j].index(i)
    else:
      cost += 10
    if i == j:
      cost += 10
    m[i][j] = cost

print('MATRIX:')
print(*m, sep='\n')
print()

# running munkres algorithm
o = Munkres()
idxs = o.compute(m)

cost = 0

# printing partnerships, these are double counted so cost is divided by 2
for a, b in idxs:
  print(num2name[a], num2name[b], 'COST: ', m[a][b])
  cost += m[a][b]

print('TOTAL COST: ', cost//2)
