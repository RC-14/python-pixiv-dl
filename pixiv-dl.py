#!/usr/bin/env python3

from genericpath import isdir, isfile
from sys import argv
import requests

def print_help():
	print(f'Usage: {argv[0][argv[0].rindex('/') + 1:]} ILLUSTRATION_ID [--out-dir OUTPUT_DIRECTORY]')
	print('\nILLUSTRATION_ID     Numeric id of the illustration to download. (https://www.pixiv.net/artworks/<Illustration ID>)')
	print('OUTPUT_DIRECTORY    The directory to write the downloaded images into.')
	print('\nProviding -- for any option will make it be read from stdin.')
	print('Specifying an option multiple times will overwrite the preceding occurrences.')
	print('Not specifying an ILLUSTRATION_ID has the same effect as --.')
	print('\nSpecifying --help will print this help message and exit.')
	exit(1)

if '--help' in argv:
	print_help()

illust_id = '--'
out_dir = './'

for i in range(1, len(argv)):
	if len(argv[i]) > 2 and argv[i].startswith('--'):
		continue

	if argv[i - 1] == '--out-dir':
		out_dir = argv[i]
		continue

	illust_id = argv[i]

if illust_id == '--':
	illust_id = input('Illustration ID (/artworks/<Illustration ID>): ')

if out_dir == '--':
	out_dir = input('Output directory: ')

if illust_id == None or not illust_id.isnumeric():
	print('Invalid Illustration ID.\n')
	print_help()

if not out_dir.endswith('/'):
	out_dir += '/'

if not isdir(out_dir):
	print(f'"{out_dir}" is not a directory.')

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
	file_path = f'{out_dir}{illust_id}-{i}.{fileType}'
	if isfile(file_path):
		print(f'File "{file_path}" already exitst.')
		continue

	url = orig_url.replace('_p0.', '_p' + f'{i}' + '.')
	img_result = requests.get(url, headers={ 'Referer': 'https://www.pixiv.net/' })
	if img_result.status_code != 200:
		print(f'Got Status Code {img_result.status_code} when downloading image {i+1} of {page_count}')
		continue
	
	try:
		with open(file_path, 'wb') as file:
			file.write(img_result.content)
			file.close()
			print(f'Saved image {i+1} of {page_count} to "{file_path}".')
	except:
		print(f'Failed to write image {i} of {page_count} to "{file_path}".')

print('Done.')
