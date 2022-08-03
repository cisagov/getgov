import csv
import requests

DOMAIN_LIST_URL = "https://raw.githubusercontent.com/cisagov/dotgov-data/main/current-full.csv"

data = requests.get(DOMAIN_LIST_URL).content.decode('utf-8')
csv_data = list(csv.reader(data.splitlines(), delimiter=','))
domains =  csv_data[1:]
fields = csv_data[0] + ['Response']

def check_status_response(domain):
    try:
        response = requests.get(f"https://{domain}", timeout=3).status_code
    except Exception as e:
        response = type(e).__name__
    return response

full_data = []
for domain in domains:
    domain_name = domain[0]
    response = check_status_response(domain_name)
    full_data.append(domain + [response])

with open('../data/response_codes.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(full_data)
