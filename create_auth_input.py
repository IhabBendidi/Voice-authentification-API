import argparse
import json
import base64


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--record", required=True,
	help="")
ap.add_argument("-b", "--voiceModel",
	help="")


args = vars(ap.parse_args())

#binary_records = []
record = args["record"]
output = {}





with open(record, 'rb') as binary_file:
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
        #binary_records.append(base64_encoded_data)
    base64_message = base64_encoded_data.decode('utf-8')
    #binary_records.append(base64_message)
    output['record'] = base64_message
        #print(base64_message)


if args["voiceModel"] is not None:
    model = args["voiceModel"]
    with open(model, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
            #binary_records.append(base64_encoded_data)
        base64_message = base64_encoded_data.decode('utf-8')
        #binary_records.append(base64_message)
        output['voiceModel'] = base64_message
#output = {'record1':binary_records[0],'record2':binary_records[1],'record3':binary_records[2]}
#print(output)
with open('auth.json', 'w+') as outfile:
    json.dump(output, outfile)
