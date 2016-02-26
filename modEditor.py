from lxml import etree
from six import string_types

def create_mod(number_of_features, nameOfMod):
	number_of_features = number_of_features
	root = etree.Element("SoftwareType")
	create_tags(root)
	add_features(root,number_of_features)
	save_mod(root,nameOfMod)

def create_tags(root):
	field_list = [
		'Name','Category', 'Description', 'Random', 'Unlock', 'OSSpecific',
		'Population',  'InHouse','Retention','Iterative','NameGenerator'
		]

	for name in field_list:
		etree.SubElement(root, name).text = ''

def add_features(root, number_of_features):
	features = etree.SubElement(root, "Features")                   
	while (number_of_features > 0):  
		feature_number = str(number_of_features)                                         
		name = 'Feature %s' %feature_number
		add_feature(features, name)
		number_of_features = number_of_features - 1  

def add_feature(features, name):
		feature = etree.SubElement(features, "Feature")         
		etree.SubElement(feature, "Name").text = name
		populate_feature(feature)

def populate_feature(feature):

	field_list = [
		'Description', 'Unlock', 'DevTime', 'Innovation',
		'Usability', 'Stability', 'CodeArt', 'Server', 'Dependencies'
		]
	for field in field_list:
		etree.SubElement(feature, field).text = ''

def save_mod(root, Name):
	saveFile = open(Name,'wb')  
	file_to_save = (etree.tostring(root,pretty_print=True))
	saveFile.write(file_to_save) 
	saveFile.close() 

def add_Dependencies(dependencies, dependency_dict_list):
	""" Adds the dependencies in a feature using dictionaries. When
		a feature is loaded, its dependencies are added to 
		dictionaries. Three for each type of software that the 
		dependencies are categorized as."""

	for dictionary in dependency_dict_list:	                                               
		for feature, software in dictionary.items():											
			if not any(dependency.text != feature for dependency in dependencies):
				etree.SubElement(dependencies,"Dependency", Software = software).text = feature  

def add_custom_dependencies(dependencies, custom_dependency_dict):
	""" This goes through the custom_Dependency_Dict and adds
		dependencies to the current feature"""

	for software, features in custom_dependency_dict.items():	
		if isinstance(features,string_types):
			etree.SubElement(dependencies,"Dependency", Software = software).text = features 
		else:
			for feature in features:
				etree.SubElement(dependencies,"Dependency", Software = software).text = feature     

def set_tag_text(dictionary, parent, t):
	for key, value in dictionary.items():	
		text = str(value.text())
		if t == "c":
			etree.SubElement(parent,key).text = text
		else: 
			parent.find(key).text = text	    

def set_field_text(parent):
	for line_edit, tag in dictionary.items():
		text = parent.find(tag).text
		line_edit.setText(text)

def set_tag_text(dictionary, parent, t):
	for key, value in dictionary.items():	
		text = str(value.text())
		if t == "c":
			etree.SubElement(parent,key).text = text
		else: 
			parent.find(key).text = text	


def add_category(self, Categories, dictionary, name):
	""" Adds a Category to the tag Categories. It then creates the
		tags needed and adds the correct text to each."""
	
	combobox = self.CATEGORYCOMBOBOX 
	name = str(self.categoryNameEdit.text())

	if Categories is not None and name:
		category = etree.SubElement(Categories, 'Category')
		set_tag_text(dicttionary, category , 'c')
		self.add_to_combobox(combobox, Categories, 'd')



