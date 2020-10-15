import bs4
import requests
import csv
import os


class Config:
    def __init__(self):
        self.baseurl = 'https://www.agedcarequality.gov.au/reports'
        self.eachurl = 'https://www.agedcarequality.gov.au'
        self.session = requests.session()
        self.path = os.path.dirname(os.path.abspath(
            __file__)) + '/homes_audit_data.csv'

    def make_file(self):
        with open(self.path, 'w', newline='') as path:
            writer = csv.writer(path)
            writer.writerow(
                ['homenames', 'home_previous', 'previous', 'racsid', 'service', 'suburbs', 'states', 'post_code',
                 'hrefdata'])

    def get_each_home(self):
        with open(self.path, 'r', newline='') as nfile:
            reader = csv.reader(nfile)
            next(reader)
            for each in reader:
                endpoint = each[8]
                data = self.session.get(
                    self.eachurl + endpoint)
                html = bs4.BeautifulSoup(data.content, 'html.parser')
                teaser_info = html.find_all('div', {'class': 'teaser__info'})
                teaser_summary = html.find_all('div', {'class': 'teaser__summary'})
                teaser_tags = html.find_all('span', {'class': 'file file--mime-application-msword file--x-office-document'})
                href = html.select('.file file--mime-application-msword file--x-office-document a')
                dates = [i.get_text().replace('\n', '') for i in teaser_info]
                summary = [i.get_text().replace('\n', '') for i in teaser_summary]
                tags = [i.get_text().replace('\n', '') for i in teaser_tags]
                hrefdata = [i['href'] for i in href]
                print(hrefdata)

    def get_audits(self):
        page = 0
        with open(self.path, 'a', newline='') as nfile:
            writer = csv.writer(nfile)
            while not page:
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
