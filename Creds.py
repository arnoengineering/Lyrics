import os
import sys
# save dir
os.chdir(os.path.dirname(sys.argv[0]))
path = os.getcwd()

if not os.path.exists('Songs'):
    os.mkdir('Songs')
csv_pre = ' Songs.csv'

# tokens
with open('MiscFiles/pass.txt', 'r') as f:
    file = f.readlines()
    token = file[1].strip()
    usr = file[3].strip()
    password = file[5].strip()
    receivers = file[7].strip().split(',')  # list of all receivers
