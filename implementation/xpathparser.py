from lxml import html
import json


class XPathParser:
    """
        This class accepts list of html page contents and transforms it
        into parsed json format
    """

    def __init__(self, sites_to_parse):
        self.sites_to_parse = sites_to_parse

        self.parsed_output = {
            'pages': []
        }

    def start(self):
        for site in self.sites_to_parse:
            if site["type"] == "rtvslo":
                self.parse_rtvslo(site["pages"])

            elif site["type"] == "overstock":
                self.parse_overstock(site["pages"])

            elif site["type"] == "avtonet":
                self.parse_avtonet(site["pages"])

        # self.write_to_file('xpath_parsed_data', self.parsed_output)

    def prettify_content(self, page_content, remove_br):
        content = page_content.replace('\t', '').replace('\n', '').replace('\r', '').replace('&nbsp;', ' ')

        if remove_br:
            content = content.replace('<br>', '')

        return ' '.join(content.split())

    def format_text(self, text):
        return text.lstrip().rstrip()

    def write_to_file(self, filename, data_to_save):
        with open('output/' + filename + '.json', 'w') as file:
            json.dump(data_to_save, file, ensure_ascii=False)

    def split_saving(self, saving):
        return saving.replace('(', '').replace(')', '').split()

    def parse_overstock(self, pages):

        pages_output = []

        for page in pages:

            page_content = {
                'type': 'overstock',
                'items': []
            }

            # First form an XML tree
            tree = html.fromstring(self.prettify_content(page, False))

            # title
            title_items = tree.xpath(
                '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/a/b/text()')
            # description
            description_items = tree.xpath(
                '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[2]/span/text()')
            # listPrice
            list_price_items = tree.xpath(
                '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()')
            # price
            price_items = tree.xpath(
                '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()')
            # saving
            saving_items = tree.xpath(
                '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()')

            for index, item in enumerate(title_items):
                item_data = {
                    'title': self.format_text(item),
                    'content': self.format_text(description_items[index]),
                    'listPrice': self.format_text(list_price_items[index]),
                    'price': self.format_text(price_items[index]),
                    'saving': self.format_text(self.split_saving(saving_items[index])[0]),
                    'savingPercentage': self.format_text(self.split_saving(saving_items[index])[1]),
                }

                page_content['items'].append(item_data)

            self.parsed_output['pages'].append(page_content)

            pages_output.append({'items': page_content['items']})

        self.write_to_file('xpath_overstock', pages_output)

    def parse_rtvslo(self, pages):

        pages_output = []

        for page in pages:
            page_content = {
                'type': 'rtvslo',
                'content': {}
            }

            # First form an XML tree
            tree = tree = html.fromstring(self.prettify_content(page, False))

            # author
            author = tree.xpath('//div[@class="author-name"]/text()')

            # publishedTime
            publishedTime = tree.xpath('//*[@id="main-container"]/div[3]/div/div[1]/div[2]/text()')

            # title
            title = tree.xpath('//header[@class="article-header"]/h1/text()')

            # subtitle
            subtitle = tree.xpath('//header[@class="article-header"]/div[@class="subtitle"]/text()')

            # lead
            lead = tree.xpath('//header[@class="article-header"]/p[@class="lead"]/text()')

            # content
            content = tree.xpath('//article[@class="article"]/p/text()')

            item_data = {
                'author': self.format_text(author[0]),
                'publishedTime': self.format_text(publishedTime[0]),
                'title': self.format_text(title[0]),
                'subtitle': self.format_text(subtitle[0]),
                'lead': self.format_text(lead[0]),
                'content': self.format_text(' '.join(content))
            }

            page_content['content'] = item_data
            self.parsed_output['pages'].append(page_content)

            pages_output.append(item_data)

        self.write_to_file('xpath_rtvslo', pages_output)

    def parse_avtonet(self, pages):

        pages_output = []

        for page in pages:

            page_content = {
                'type': 'avtonet',
                'content': {}
            }

            tree = html.fromstring(self.prettify_content(page, True))

            # title
            title = tree.xpath('//div[@class="OglasDataTitle"]/h1/text()')

            # decription
            description = tree.xpath('//div[@class="OglasDataTitle"]/h1/small/text()')

            # price
            has_action_price = tree.xpath('//p[@class="OglasDataAkcijaCena"]')

            if not has_action_price:
                price = tree.xpath('//p[@class="OglasDataCenaTOP"]/text()')
            else:
                ## action price
                price = tree.xpath('//p[@class="OglasDataStaraCena"]/span/text()')
                sale_price = tree.xpath('//p[@class="OglasDataAkcijaCena"]/span/text()')

            # seller
            seller = tree.xpath('//div[@class="Padding14 Bold"]/text()')

            # year
            year = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[3]/div[@class="OglasDataRight"]/text()')

            # mileage
            mileage = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[6]/div[@class="OglasDataRight"]/text()')

            # fuel type
            fuel_type = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[7]/div[@class="OglasDataRight"]/text()')

            # enginge
            engine = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[8]/div[@class="OglasDataRight"]/text()')

            # transmission
            transmission = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[9]/div[@class="OglasDataRight"]/text()')

            # color
            color = tree.xpath(
                '//div[@class="OglasWrapper RoundedBottom MarginBTM"]/div[11]/div[@class="OglasDataRight"]/text()')

            item_data = {
                'title': self.format_text(title[0]),
                'description': self.format_text(description[0]),
                'price': self.format_text(price[0]),
                'seller': self.format_text(seller[0]),
                'year': self.format_text(year[0]),
                'mileage': self.format_text(mileage[0]),
                'fuel_type': self.format_text(fuel_type[0]),
                'engine': self.format_text(engine[0]),
                'transmission': self.format_text(transmission[0]),
                'color': self.format_text(color[0])
            }

            if has_action_price:
                item_data['sale_price'] = sale_price[0]

            page_content['content'] = item_data
            self.parsed_output['pages'].append(page_content)

            pages_output.append(item_data)

        self.write_to_file('xpath_avto_net', pages_output)
