import bs4
import requests
import csv
import os
import re


# from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


class Config:
    def __init__(self):
        self.baseurl = 'https://www.agedcarequality.gov.au/reports'
        self.eachurl = 'https://www.agedcarequality.gov.au'
        self.session = requests.session()
        self.path = os.path.dirname(os.path.abspath(
            __file__)) + '/homes_audit_data.csv'
        self.path_2 = os.path.dirname(os.path.abspath(
            __file__)) + '/homes_audit_data_v2.csv'
        self.path_3 = os.path.dirname(os.path.abspath(
            __file__)) + '/homes_audit_data_v3.csv'

    def make_file(self):
        with open(self.path, 'w', newline='') as path:
            writer = csv.writer(path)
            writer.writerow(
                ['homenames', 'home_previous', 'previous', 'racsid', 'service', 'suburbs', 'states', 'post_code',
                 'hrefdata'])

    def make_file_v2(self):
        with open(self.path_2, 'w', newline='') as npath:
            writer = csv.writer(npath)
            writer.writerow(
                ['homenames', 'dates', 'summary', 'links'])

    def get_each_file(self):
        with open(self.path_2, 'r', newline='') as rfile:
            reader = csv.reader(rfile)
            next(reader)
            for each in reader:
                name = each[0].replace(' ', '_').replace(',', '').replace('/', '')
                date = each[1].replace(' ', '_').replace(',', '').replace('/', '')
                endpoint = each[3]
                endpoint_file = re.compile('[a-zA-Z-0-9-]+.doc|[a-zA-Z-0-9-]+.pdf|[a-zA-Z0-9-]+.doc|[a-zA-Z0-9-]+.pdf')
                try:
                    files = endpoint_file.findall(endpoint).pop()
                except IndexError:
                    pass
                data = self.session.get(
                    'https://www.agedcarequality.gov.au' + endpoint)
                with open('files/{}'.format(str(name)) + '_{}'.format(str(date)) + '_{}'.format(str(files)),
                          'wb') as newsfile:
                    newsfile.write(data.content)
                    print("writing file")
                    print(files)

    def get_each_home(self):
        with open(self.path, 'r', newline='') as nfile, open(self.path_2, 'w', newline='') as writefile:
            writer = csv.writer(writefile)
            reader = csv.reader(nfile)
            next(reader)
            for each in reader:
                home_name = each[0]
                endpoint = each[8]
                data = self.session.get(
                    self.eachurl + endpoint)
                html = bs4.BeautifulSoup(data.content, 'html.parser')
                teaser_info = html.find_all('div', {'class': 'teaser__info'})
                teaser_summary = html.find_all('div', {'class': 'teaser__summary'})
                href = html.select('.field__items a')
                dates = [i.get_text().replace('\n', '') for i in teaser_info]
                summary = [i.get_text().replace('\n', '') for i in teaser_summary]
                links = [i['href'].replace('https://www.agedcarequality.gov.au', '') for i in href]
                clist = [
                    {'dates': j, 'summary': k, 'links': l}
                    for j, k, l in
                    zip(dates, summary, links)]
                for lis in clist:
                    writer.writerow([home_name,
                                     lis['dates'],
                                     lis['summary'],
                                     lis['links']])
                    print('writing row')
                    print(home_name)

    def get_fraction_audit(self):
        with open(self.path_2, 'r', newline='') as rfile, open(self.path_3, 'w', newline='') as nfile:
            reader = csv.reader(rfile)
            writer = csv.writer(nfile)
            audit_fraction = re.compile('[0-9]+.of.the.[0-9]+')
            for each in reader:
                home_name = each[0]
                date = each[1]
                try:
                    audit = audit_fraction.findall(each[2]).pop()
                    print(audit)
                except IndexError:
                    pass
                writer.writerow([home_name, date, audit])

    def get_audits(self):
        page = 0
        with open(self.path, 'a', newline='') as nfile:
            writer = csv.writer(nfile)
            while True:
                data = self.session.get(
                    self.baseurl + '?name=&racs_id=&suburb&state=All&prov_name=&service_type=All&previous_names=&postcode=&page={}'.format(
                        str(page)))
                html = bs4.BeautifulSoup(data.content, 'html.parser')
                home_name = html.find_all('h3', {'class': 'field-content'})
                provider_name = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-prov-name'})
                previous_names = html.find_all('div', {'class': 'views-field views-field-nothing'})
                racs = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-racs-key'})
                service_type = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-type'})
                suburb = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-suburb'})
                state = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-state'})
                post = html.find_all('div', {'class': 'views-field views-field-field-acqsc-service-postcode'})
                href = html.select('.field-content a')
                hrefdata = [i['href'] for i in href]
                homenames = [i.get_text() for i in home_name]
                home_previous = [i.get_text().replace('\n', '').replace('Provider name: ', '') for i in provider_name]
                previous = [i.get_text().replace('Previous service names:\n', '').replace('\n', '') for i in
                            previous_names]
                racsid = [i.get_text().replace('RACS/Commission ID: ', '').replace('\n', '') for i in racs]
                service = [i.get_text().replace('Service type: ', '').replace('\n', '') for i in service_type]
                suburbs = [i.get_text().replace('Suburb: ', '').replace('\n', '') for i in suburb]
                states = [i.get_text().replace('State: ', '').replace('\n', '') for i in state]
                post_code = [i.get_text().replace('Postcode: ', '').replace('\n', '') for i in post]
                clist = [
                    {'homenames': i, 'home_previous': j, 'previous': k, 'racsid': l, 'service': m, 'suburbs': n,
                     'states': b,
                     'post_code': v, 'hrefdata': u}
                    for i, j, k, l, m, n, b, v, u in
                    zip(homenames, home_previous, previous, racsid, service, suburbs, states, post_code, hrefdata)]
                for each in clist:
                    writer.writerow([each['homenames'],
                                     each['home_previous'],
                                     each['previous'],
                                     each['racsid'],
                                     each['service'],
                                     each['suburbs'],
                                     each['states'],
                                     each['post_code'],
                                     each['hrefdata']])
                    print('writing row')
                if len(clist) == 0:
                    break
                else:
                    print(len(clist))
                    page += 1
