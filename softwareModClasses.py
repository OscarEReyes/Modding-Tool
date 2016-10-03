from softwareObject import SoftwareObject
from Dependency import Dependency
from SoftwareCategory import SoftwareCategory

class Category(SoftwareObject):
    line_tags = [
        'Description',
        'Unlock',
        'Popularity',
        'Retention',
        'TimeScale',
        'Iterative',
        'NameGenerator'
    ]

    check_tags = [
        'Unlock'
        'NameGenerator'
    ]

    def __init__(self, parent, name, combobox, scan=False):
        SoftwareObject.__init__(self, parent, name, combobox)
        if scan:
            self.instantiate_object()

        else:
            if not any(element.attrib['Name']== self.name for element in self.parent):
                self.create_element('category')


class Feature(SoftwareObject):
    line_tags = [
        'Category',
        'Description',
        'Unlock',
        'DevTime',
        'Innovation',
        'Usability',
        'Stability',
        'CodeArt',
        'Server'
    ]

    check_tags = [
        'Server',
        'Unlock',
        'Category'
    ]

    def __init__(self, features, name, combobox, scan=False):
        SoftwareObject.__init__(self, features, name, combobox)
        self.dependencies = {}
        self.software_categories = {}
        if scan:
            self.instantiate_object()

        else:
            if not any(element.find("Name").text == self.name for element in self.parent):
                self.create_element('feature')

    def rename(self, name):
        """
        * Parameter: name (str)
        * Set feature's (etree element) 'Name' tag text value to name
        * Rename current feature_combobox item to name parameter.
        """

        self.name = name
        feature = self.inventory[self]
        feature.find('Name').text = name
        # Renames on combobox
        index = self.combobox.currentIndex()
        self.combobox.setItemText(index, self.name)

    def check_attribute(self, attributes, from_text):
        """
        * Takes in parameter attributes (dict)
        * Takes in from_text parameter (line_edit)
        * Check each attribute in attributes
        * If status is True, add attribute
        * Text is 'TRUE' for all attributes except the 'From' attribute
        * If status is False, delete attribute
        """

        for attribute, status in attributes.items():
            text = from_text if attribute == 'From' else 'TRUE'
            if status:
                self.add_attribute(attribute, text)
            else:
                self.delete_attribute(attribute)

    def add_attribute(self, attrib, text):
        """
        * Takes in attrib parameter (str)
        * Takes in text parameter (str)
        * Add attribute if it isn't in feature's attrib (list)
        """

        feature = self.inventory[self]
        if attrib not in feature.attrib:
            feature.attrib[attrib] = text

    def delete_attribute(self, attrib):
        """
         * Take in attrib parameter (str)
         * Remove attribute if it isn't in feature's attrib (list)
         """

        feature = self.inventory[self]
        if attrib in feature.attrib:
            del feature.attrib[attrib]

    def add_special_tag(self, tag_type, name, tag_descriptor, combobox):
        """
        * Takes in tag_type parameter (str)
        * Takes in name parameter (str)
        * Takes in tag_descriptor parameter
        * Create a type_object (Software Category or Dependency Object)
        * Store type_object in tag_list[tag_descriptor]
        """

        tag_list = self.software_categories if tag_type == 'sc' else self.dependencies
        if tag_descriptor not in tag_list:
            feature = self.inventory[self]
            if tag_type == 'sc':
                type_object = SoftwareCategory(feature, name, tag_descriptor)
            else:
                type_object = Dependency(feature, name, tag_descriptor)

            tag_list[tag_descriptor] = type_object

    def scan_special_tag(self, tag_type, name, tag_descriptor):
        """
        * Same as add_special tag, but meant for scanning.
        * Always creates Dependency or Software Category object
        * Passes scan as True to add method.
        """

        tag_list = self.software_categories if tag_type == 'sc' else self.dependencies
        feature = self.inventory[self]
        if tag_type == 'sc':
            type_object = SoftwareCategory(feature, name, tag_descriptor, True)
        else:
            type_object = Dependency(feature, name, tag_descriptor, True)
        tag_list[tag_descriptor] = type_object

    def delete_special_tag(self, tag_type, tag_descriptor, combobox):
        """
        * Parameter: tag_type (str)
        * Parameter: tag_descriptor (str)
        * Delete object (Dependency or Software Category Object)
        * depending on tag_type
        * Pop tag_descriptor key in tag_dict
        """

        tag_dict = self.software_categories if tag_type == 'sc' else self.dependencies
        feature = self.inventory[self]

        if tag_type == 'sc':
            SoftwareCategory.delete_category(feature, tag_descriptor)
        else:
            Dependency.delete_dependency(feature, tag_descriptor)

        tag_dict.pop(tag_descriptor)
        current_index = combobox.currentIndex()
        combobox.removeItem(current_index)
