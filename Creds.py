# tokens
with open('pass.txt', 'r') as f:
    file = f.readlines()
    token = file[1].strip()
    usr = file[3].strip()
    password = file[5].strip()
    receivers = file[7].strip().split(',')  # list of all receivers
