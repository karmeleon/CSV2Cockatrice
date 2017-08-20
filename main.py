import argparse
import csv
import xml.etree.cElementTree as ET
from os import listdir
from os.path import isfile, join

def main():
	parser = argparse.ArgumentParser(description='Generates a Cockatrice cards.xml from CSV files.')
	parser.add_argument('csv_path', metavar='csv_path', type=str, help='Path to folder containing CSV files.')

	args = parser.parse_args()

	root = ET.Element('cockatrice_carddatabase', version='3')
	cards = ET.SubElement(root, 'cards')

	csv_path_list = find_csv_files(args.csv_path)
	print('Found CSV files: {}'.format(','.join(csv_path_list)))

	parse_cards_from_csv(csv_path_list, cards)

	tree = ET.ElementTree(root)
	tree.write('cards.xml')

def find_csv_files(csv_path):
	"""
	Gets a list of paths to all CSV files found within the given path.

	:param csv_path: A string path to a folder to look in
	:returns: A list of paths to CSV files that are direct children of the given folder.
	"""
	# <3 list comprehension
	return [join(csv_path, f) for f in listdir(csv_path) if isfile(join(csv_path, f)) and f.endswith('.csv')]

def parse_cards_from_csv(csv_path_list, cards):
	"""
	Reads a list of CSV files and adds each line to the cards XML tree.

	:param csv_path_list: List of paths to CSV files
	:param cards: <cards> XML SubElement
	"""
	for csv_path in csv_path_list:
		with open(csv_path) as csv_file:
			csv_reader = csv.DictReader(csv_file)
			print('Reading file {}'.format(csv_path))
			for csv_line in csv_reader:
				add_card_to_document(cards, csv_line, csv_path)

def add_card_to_document(cards, csv_line, csv_name):
	"""
	Adds a new card to the <cards> element.

	:param cards: <cards> SubElement
	:param csv_line: Dict representing a CSV line to transform.
	:param csv_name: Name of the CSV file this line came from.
	"""
	card = ET.SubElement(cards, 'card')

	name = ET.SubElement(card, 'name').text = csv_line['name']
	pic_url = ET.SubElement(card, 'set', picURL='{}.png'.format(csv_line['id'])).text = csv_line['set']
	# the mana cost is the spell level if a spell, otherwise it's nothing?
	computed_mana_cost = csv_line['level'] if 'spell' in csv_name else ''
	manacost = ET.SubElement(card, 'manacost').text = computed_mana_cost
	cmc = ET.SubElement(card, 'cmc').text = computed_mana_cost

	type_parts = [
		csv_line.get('school', None),
		csv_line.get('school1', None),
		csv_line.get('school2', None),
		csv_line.get('type', None),
	]

	type_parts = [part for part in type_parts if part is not None]

	computed_type = ' '.join(type_parts)
	type = ET.SubElement(card, 'type').text = computed_type

	computed_pt = '{}/ AC{}'.format(csv_line['hp'], csv_line['ac']) if 'creature' in csv_name else None
	pt = ET.SubElement(card, 'pt').text = computed_pt

	if 'component' in csv_name:
		if csv_line['type'] == 'Component':
			computed_tablerow = '0'
		else:
			computed_tablerow = '1'
	elif 'creature' in csv_name:
		computed_tablerow = '2'
	elif 'spell' in csv_name:
		computed_tablerow = '3'
	else:
		# shouldn't ever happen, but catch it just in case
		computed_tablerow = '-1'
	tablerow = ET.SubElement(card, 'tablerow').text = computed_tablerow

	if 'creature' in csv_name:
		computed_text = '{} STR, {} DEX, {} CON, {} INT, {} WIS, {} CHA, {}'.format(
			csv_line['str'],
			csv_line['dex'],
			csv_line['con'],
			csv_line['int'],
			csv_line['wis'],
			csv_line['cha'],
			csv_line['desc'],
		)
	else:
		computed_text = csv_line['desc']

	text = ET.SubElement(card, 'text').text = computed_text

if __name__ == '__main__':
	main()