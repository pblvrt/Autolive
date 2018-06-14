import sys
from models import Channel_settings
from config import Config


''' Get input streamkey '''
try:
    input_key=sys.argv[1]
except:
    print("please provide streamkey")
    sys.exit(0)

''' init config, channel '''
config = Config(input_key)
data = config.load_data()

print(data)
the_list = []
for i in data[0]['logs']:
    the_list.append(float(i))

max_number = max(the_list)
last = data[0]['logs'][str(max_number)]
print(last['Status'])
