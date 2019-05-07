from xpathparser import XPathParser
from RegexParser import RegexParser
from RoadRunner import RoadRunner

overstock_page_1 = open('input/overstock.com/jewelry01.html', 'r').read()
overstock_page_2 = open('input/overstock.com/jewelry02.html', 'r').read()

rtvslo_page_1 = open('input/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html', 'r').read()
rtvslo_page_2 = open('input/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html',
                    'r').read()

avtonet_page_1 = open('input/avto.net/mercedes-benz-e.html', 'r').read()
avtonet_page_2 = open('input/avto.net/ford-galaxy.html', 'r').read()

sites_to_parse = [
    {
        'type': 'overstock',
        'pages': [overstock_page_1, overstock_page_2]
    },
    {
        'type': 'rtvslo',
        'pages': [rtvslo_page_1, rtvslo_page_2]
    },
    {
        'type': 'avtonet',
        'pages': [avtonet_page_1, avtonet_page_2]
    }
]

xpath_parser = XPathParser(sites_to_parse)

xpath_parser.start()

regex_parser = RegexParser(sites_to_parse)

regex_parser.start()

roadrunner = RoadRunner(sites_to_parse)

roadrunner.start()
