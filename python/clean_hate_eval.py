import csv
import os


# create dir for hate and no hate
if not os.path.exists('/Users/fedeiman/Desktop/python/hate'):
    os.makedirs('/Users/fedeiman/Desktop/python/hate')
if not os.path.exists('/Users/fedeiman/Desktop/python/no_hate'):
    os.makedirs('/Users/fedeiman/Desktop/python/no_hate')

# if HS column has 1 is hate so go to hate dir
# if HS column has 0 is no hate so go to no_hate dir

with open('hateval2019_en_train.csv') as csvfile:
     reader = csv.DictReader(csvfile)
     id_hate = 0
     id_no_hate = 0
     for row in reader:
        if(row['HS'] == "1"):
            with open('/Users/fedeiman/Desktop/python/hate/{}'.format(id_hate), 'w') as f:
                id_hate = id_hate + 1
                f.write(row['text'])
        if(row['HS'] == "0"):
            with open('/Users/fedeiman/Desktop/python/no_hate/{}'.format(id_no_hate), 'w') as f:
                id_no_hate = id_no_hate + 1
                f.write(row['text'])