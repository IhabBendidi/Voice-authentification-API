import argparse
import json
import base64


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--record1", required=True,
	help="")
ap.add_argument("-b", "--record2", required=True,
	help="")
ap.add_argument("-c", "--record3", required=True,
	help="")

args = vars(ap.parse_args())
records = []
binary_records = []
records.append(args["record1"])
records.append(args["record2"])
records.append(args["record3"])

for path in records :
    with open(path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        #binary_records.append(base64_encoded_data)
        base64_message = base64_encoded_data.decode('utf-8')
        binary_records.append(base64_message)
        #print(base64_message)
output = {'record1':binary_records[0],'record2':binary_records[1],'record3':binary_records[2]}
#print(output)
with open('enrollement.json', 'w+') as outfile:
    json.dump(output, outfile)
