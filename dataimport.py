import csv, os, sys
print sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
print settings
from apps.chargen.models import *
 
#iterate through the items in the CSV file,
#updating or inserting into Django db as necessary
 
def runit():
	
	#change file name manually here
    INPUT_FILE = 'weapons.txt'
     
    reader = csv.reader(open(INPUT_FILE), delimiter=",", quotechar='"')
     
    for row in reader:
        
        #change column mapping manually here
        item = Weapon(name=row[0], allowed_classes=row[1])
           
        try:
            item.save()
            print item.name
        except Exception, ex:
            print ex
            break
