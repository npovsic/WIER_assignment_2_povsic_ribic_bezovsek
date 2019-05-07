import re
import json
from bs4 import BeautifulSoup


class RegexParser:

    def __init__(self, sites_to_parse):
        self.sites_to_parse = sites_to_parse

    def start(self):
        for site in self.sites_to_parse:
            if site["type"] == "rtvslo":
                self.parse_rtvslo(site["pages"])

            elif site["type"] == "overstock":
                self.parse_overstock(site["pages"])

            elif site["type"] == "avtonet":
                self.parse_avtonet(site["pages"])

    def get_text(self, html):
        soup = BeautifulSoup(html, 'lxml')
        return soup.get_text().lstrip().rstrip()

    def remove_tags(self, html, tags):
        soup = BeautifulSoup(html, 'lxml')
        [s.extract() for s in soup(tags)]
        return str(soup)

    def write_to_file(self, filename, data_to_save):
        with open('output/' + filename + '.json', 'w') as file:
            json.dump(data_to_save, file, ensure_ascii=False)

    def parse_rtvslo(self, pages):
        data_to_save = []

        for page in pages:
            page_content = self.remove_tags(" ".join(page.split()).replace('> <', '><'), [ "script", "figure" ])

            header_regex = r"<header class=\"article-header\">(.*?)<h1>(.*?)<\/h1><div class=\"subtitle\">(.*?)<\/div>(.*?)<p class=\"lead\">(.*?)<\/p>"
            header_match = re.compile(header_regex).search(page_content)

            title = header_match.group(2)
            subtitle = header_match.group(3)
            lead = header_match.group(5)

            meta_regex = r"<div class=\"article-meta\">(.*?)<div class=\"author-name\">(.*?)<\/div>(.*?)<div class=\"publish-meta\">(.*?)<br\/>(.*?)<\/div>"
            meta_match = re.compile(meta_regex).search(page_content)

            author = meta_match.group(2)
            published_time = meta_match.group(4)

            article_regex = r"<article class=\"article\">(.*)<\/article>"
            article = re.compile(article_regex).search(page_content)
            content = self.get_text(article.group(1))

            data_to_save.append({
                "author": author.lstrip().rstrip(),
                "published_time": published_time.lstrip().rstrip(),
                "title": title.lstrip().rstrip(),
                "subtitle": subtitle.lstrip().rstrip(),
                "lead": lead.lstrip().rstrip(),
                "content": content.lstrip().rstrip(),
            })

        self.write_to_file("regex_rtvslo", data_to_save)

    def parse_overstock(self, pages):
        data_to_save = []

        for page in pages:
            page_content = self.remove_tags(" ".join(page.split()).replace('> <', '><'), [ "script" ])

            regex = r"<td valign=\"top\"><a href=\"(.*?)\">(.*?)<\/a><br\/><table><tbody><tr><td valign=\"top\"><table><tbody>(.*?)<\/tbody><\/table><\/td><td valign=\"top\"><span (.*?)>(.*?)<br\/>(.*?)<\/span>(.*?)<\/td><\/tr><\/tbody><\/table><\/td>"

            items = []

            for item in re.finditer(regex, page_content):
                title = self.get_text(item.group(2))
                prices_info = item.group(3)
                content = self.get_text(item.group(5))

                list_price_regex = r"<tr>(.*?)<td align=\"left\" (.*?)><s>(.*?)<\/s><\/td><\/tr>"
                list_price_match = re.compile(list_price_regex).search(prices_info)
                list_price = self.get_text(list_price_match.group(3))

                price_regex = r"<tr>(.*?)<td align=\"left\" (.*?)><span class=\"bigred\">(.*?)<\/span><\/td><\/tr>"
                price_match = re.compile(price_regex).search(prices_info)
                price = self.get_text(price_match.group(3))

                saving_regex = r"<tr>(.*?)<td align=\"left\" (.*?)><span class=\"littleorange\">(\$(\d|\.|,)+) \((\d*%)\)<\/span><\/td><\/tr>"
                saving_match = re.compile(saving_regex).search(prices_info)
                saving = self.get_text(saving_match.group(3))
                saving_percent = self.get_text(saving_match.group(5))

                items.append({
                    "title": title,
                    "list_price": list_price,
                    "price": price,
                    "saving": saving,
                    "saving_percent": saving_percent,
                    "content": content,
                })

            data_to_save.append({
                "items": items
            })

        self.write_to_file("regex_overstock", data_to_save)

    def parse_avtonet(self, pages):
        data_to_save = []

        for page in pages:
            page_content = " ".join(page.split()).replace('> <', '><')

            title_regex = r"<div class=\"OglasDataTitle\"><h1>(.*?)<small>(.*?)<\/small><\/h1><\/div>"
            title_match = re.compile(title_regex).search(page_content)
            title = self.get_text(title_match.group(1))
            subtitle = self.get_text(title_match.group(2))

            price_regex = r"<div class=\"OglasDataCena (.*?)\">(.*)<p class=\"(OglasDataStaraCena|OglasDataCenaTOP)\">(.*?)<\/p>(<p class=\"OglasDataAkcijaCena\">(.*?)<span>(.*?)<\/span><\/p>)?(.*?)<\/div>"
            price_match = re.compile(price_regex).search(page_content)
            price = self.get_text(price_match.group(4)).lstrip().rstrip()

            seller_regex = r"<div class=\"Padding14 Bold\">(.*?)<\/div>"
            seller_match = re.compile(seller_regex).search(page_content)
            seller = self.get_text(seller_match.group(1))

            car_data = {
                "title": title,
                "subtitle": subtitle,
                "price": price,
                "seller": seller,
            }

            sale_price = price_match.group(7)
            if sale_price is not None:
                sale_price = self.get_text(price_match.group(7)).lstrip().rstrip()
                car_data["sale_price"] = sale_price

            data_regex = r"<div class=\"OglasData\"><div class=\"OglasDataLeft\">(.*?)<\/div><div class=\"OglasDataRight\">(.*?)<\/div>"

            for item in re.finditer(data_regex, page_content):
                attr = item.group(1).lower().replace(":", "").replace(" ", "_").replace("ž", "z").replace("č","c").replace("š", "s")
                value = item.group(2)

                if attr == "letnik":
                    car_data["year"] = value

                elif attr == "prevozeni_km":
                    car_data["mileage"] = value

                elif attr == "gorivo":
                    fuel_type = self.get_text(value)
                    car_data["fuel_type"] = fuel_type

                elif attr == "motor":
                    engine = self.get_text(value)
                    car_data["engine"] = engine

                elif attr == "menjalnik":
                    car_data["transmission"] = value

                elif attr == "barva":
                    color = self.get_text(value)
                    car_data["color"] = color

            data_to_save.append(car_data)

        self.write_to_file("regex_avto_net", data_to_save)
