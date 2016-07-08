from lxml import etree
from softwareObject import SoftwareObject


class Categories:
    category_list = []

    def __init__(self, parent, combobox, scan):
        self.parent = parent
        self.combobox = combobox
        # Add category to root
        if not scan:
            parent.insert(5, etree.Element("Categories"))
        self.categories = parent.find('Categories')

    @classmethod
    def add(cls, parent, combobox, scan=False):
        return cls(parent, combobox, scan)

    @classmethod
    def clear_inventory(cls):

        cls.category_list.clear()

    @classmethod
    def find_category(cls, name):
        """ Takes str name
            Compares the instance variable name of each category in the class list category_list
            Returns the category that makes the comparison true.
        """
        for category in cls.category_list:
            if category.name == name:
                return category

    def delete(self):
        """ Deletes categories
            Clears combobox and class list category_list
            Removes categories from self.parent """

        self.combobox.clear()
        self.category_list.clear()
        self.parent.remove(self.categories)

    def scan_category(self, name):
        """ Takes str name
            Adds name to self.combobox
            Creates a Category object of Name name
            Appends category object to category_list """

        self.combobox.addItem(name)
        category = Category.add(self.categories, name)
        self.category_list.append(category)

    def add_category(self, name):
        if not any(category.attrib["Name"] == name for category in self.categories):
            category = Category.add(self.categories, name)
            self.combobox.addItem(name)
            self.category_list.append(category)

    def delete_category(self, category):
        self.category_list.remove(category)
        category.delete(self.combobox)

        category_element = Category.inventory[category]
        self.categories.remove(category_element)


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

    def __init__(self, parent, name, scan):
        SoftwareObject.__init__(self, parent, name)
        if self not in self.inventory:
            self.inventory[self] = name
        if not scan:
            self.create_category(name)

    @classmethod
    def add(cls, parent, name, scan=False):
        return cls(parent, name, scan)

    def create_category(self, name):
        category = etree.SubElement(self.parent, "Category", Name=name)
        self.inventory[self] = category
        self.set_tags(category)

    def set_tags(self, element):
        for field in self.line_tags:
            etree.SubElement(element, field)
            self.set_etree_element_text()


class Feature(SoftwareObject):
    line_tags = [
        'Description',
        'Unlock',
        'DevTime',
        'Innovation',
        'Usability',
        'Stability',
        'CodeArt',
        'Server'
    ]

    def __init__(self, features, name, combobox):
        self.combobox = combobox
        SoftwareObject.__init__(self, features, name)
        self.dependencies = {}
        self.check_inventory()
        self.check_parent()

    @classmethod
    def add(cls, features, name, combobox):
        feature = cls(features, name, combobox)
        return feature

    def find_feature(self):
        """ Returns an etree element ('Feature') in the instance variable of parent
            (In this case a etree element called 'Features')
            with a 'Name' tag text equal to the instance variable name """

        for feature in self.parent:
            if feature.find('Name').text == self.name:
                return feature

    def check_inventory(self):
        if not any(feature.name == self.name for feature in self.inventory):
            feature = self.find_feature()
            self.inventory[self] = feature
            self.combobox.addItem(self.name)

    def check_parent(self):
        if not any(feature.find("Name").text == self.name for feature in self.parent):
            self.create_feature()

    def create_feature(self):
        """ Creates a 'Feature' etree Element  """

        feature = etree.SubElement(self.parent, "Feature")
        etree.SubElement(feature, "Name").text = self.name
        for tag in self.line_tags:
            etree.SubElement(feature, tag).text = tag

    def rename(self, name):
        self.name = name
        feature = self.inventory[self]
        feature.find('Name').text = name
        self.rename_on_combobox()

    def rename_on_combobox(self):
        index = self.combobox.currentIndex()
        self.combobox.setItemText(index, self.name)

    def check_attribute(self, attributes, from_text):
        for attribute, status in attributes.items():
            text = from_text if attribute == 'From' else 'TRUE'
            if status:
                self.add_attribute(attribute, text)
            else:
                self.delete_attribute(attribute)

    def add_attribute(self, attrib, text):
        feature = self.inventory[self]
        if attrib not in feature.attrib:
            feature.attrib[attrib] = text

    def delete_attribute(self, attrib):
        feature = self.inventory[self]
        if attrib in feature.attrib:
            del feature.attrib[attrib]

    def add_dependency(self, software, dep_feature):
        if dep_feature not in self.dependencies:
            feature = self.inventory[self]
            dependency = Dependency(feature, software, dep_feature)
            self.dependencies[dep_feature] = dependency

    def delete_dependency(self, dep_feature):
        if any(dep.feature == dep_feature for dep in self.dependencies):
            feature = self.inventory[self]
            dependency = feature.dependencies[dep_feature]
            Dependency.delete_dependency(feature, dependency.feature)
            self.dependencies.pop(dep_feature)


class Dependency:
    def __init__(self, parent, software, feature):
        self.parent = parent
        self.software = software
        self.feature = feature
        self.create_dependency()

    @classmethod
    def delete_dependency(cls, parent, feature):
        dependency = cls.find_dependency(parent, feature)
        feature.dependencies.remove(dependency)
        parent.remove(dependency)

    @classmethod
    def find_dependency(cls, parent, feature):
        for dependency in parent:
            if dependency.text == feature:
                return dependency

    def create_dependency(self):
        etree.SubElement(self.parent, "Dependency", Software=self.software).text = self.feature

