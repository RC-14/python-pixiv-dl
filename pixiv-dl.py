#!/usr/bin/env python3

from genericpath import isfile
import requests

illust_id = 34512986

url = f'https://www.pixiv.net/ajax/illust/{illust_id}?lang=en'

api_result = requests.get(url)

try:
	api_response = api_result.json()
except:
	print('Didn\'t get a JSON result. Maybe Cloudflare blocked the request?')
	exit(1)

if api_response.get('error'):
	print(f'Got an error from the pixiv API: ' + api_response.get('message'))
	exit(1)

illust_info = api_response.get('body')
orig_url = illust_info.get('urls').get('original')

if orig_url == None:
	print('Couldn\'t get an image url. Maybe the work is age restricted?')
	exit(1)

page_count = illust_info.get('pageCount')
fileType = orig_url[orig_url.rindex('.')+1:]

for i in range(0, page_count):
	file_name = f'{illust_id}-{i}.{fileType}'
	if isfile(file_name):
		print(f'File "{file_name}" already exitst.')
		continue

	url = orig_url.replace('_p0.', '_p' + f'{i}' + '.')
	img_result = requests.get(url, headers={ 'Referer': 'https://www.pixiv.net/' })
	if img_result.status_code != 200:
		print(f'Got Status Code {img_result.status_code} when downloading image {i+1} of {page_count}')
		continue

	with open(file_name, 'wb') as file:
		file.write(img_result.content)
		file.close()
		print(f'Saved image {i+1} of {page_count} to "{file_name}".')

print('Done.')
