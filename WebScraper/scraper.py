#!/usr/bin/env python

import argparse
import sys
import requests
import re
from HTMLParser import HTMLParser

# create a subclass and override the handler methods


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        if(tag == 'img' or tag == 'a'):
            self.data.append(attrs[0][1])

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


def get_webpage_text(url):
    res = requests.get(url)
    return res.text


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Provide a url')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args:
        parser.print_usage()
        sys.exit(1)

    url = args.url
    webtext = get_webpage_text(url).encode('ascii')
    url_list = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', webtext)

    email_list = re.findall(
        "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", webtext)
    phone_list = re.findall(
        '1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?', webtext)
    # print(url_list)

    parser = MyHTMLParser()
    parser.feed('<html><head><title>Test</title></head>'
                '<body><h1 class="header">Parse me!</h1><a href="https://www.google.com">google</a></body></html>')
    if len(set(url_list + parser.data)):
        print('URLs:')
        for cururl in set(url_list + parser.data):
            print(cururl)
    if len(set(email_list)):
        print('Emails:')
        for curemail in set(email_list):
            print(curemail)
    if len(set(phone_list)):
        print('Phone Numbers:')
        for curphone in set(phone_list):
            phonenumber = '-'.join(curphone).strip()
            print(phonenumber[:-2])


if __name__ == '__main__':
    main()
