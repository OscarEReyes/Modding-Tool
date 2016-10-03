from lxml import etree


class SoftwareObject:
    inventory = {}
    line_tags = []
    check_tags = []

    def __init__(self, parent, name, combobox):
        self.parent = parent
        self.name = name
        self.combobox = combobox

    @classmethod
    def add(cls, parent, name, combobox, scan=False):
        return cls(parent, name, combobox, scan)

    @classmethod
    def find_by_name(cls, name):
        for Object in cls.inventory:
            if Object.name == name:
                return Object

    @classmethod
    def set_field_dicts(cls, line_fields):
        cls.fieldDict = dict(zip(cls.line_tags, line_fields))

    def find_object(self):
        """
        * Return an etree element in instance variable of parent
        * with a 'Name' tag text equal to instance var name
        """

        for child in self.parent:
            try:
                if child.find('Name').text == self.name:
                    return child
            except AttributeError:
                if child.attrib['Name'] == self.name:
                    return child

    def instantiate_object(self):
        """
        * Check for instance of Object calling this method
        * with same name instance variable.
        *
        * If none found: look for an etree element with name tag equal
        * to instance's name variable.
        *
        * Store in self.inventory.
        * Add to self.combobox.
        """

        software_object = self.find_object()
        self.inventory[self] = software_object
        self.combobox.addItem(self.name)

    def create_element(self, element_type):
        """
        * Parameter: element_type (str)
        * Create an etree Element with tag 'Feature' or 'Category'
        * Store element in instance variable inventory (dict)
        * Set tags for element
        * Add instance variable name (str) to self.combobox
        """

        if element_type == 'feature':
            element = etree.SubElement(self.parent, "Feature")
            etree.SubElement(element, "Name").text = self.name

        else:
            element = etree.SubElement(self.parent, "Category", Name=self.name)

        self.inventory[self] = element
        self.set_tags(element)
        self.combobox.addItem(self.name)

    def delete(self):
        """
        * Get current index for self.combobox (Qt Combobox item)
        * Remove current selected item (Using var current_index)
        * Remove element from self.parent (An etree element)
        * Pop self from self.inventory
        """

        index = self.combobox.currentIndex()
        self.combobox.removeItem(index)

        element = self.inventory[self]
        self.parent.remove(element)
        self.inventory.pop(self)

    def set_tags(self, element):
        """
        * Parameter: element (etree element)
        * Iterate over tags in instance var line_tags (list)
        * Create child tag (Parent element) with a tag equal to tag
        * Set child's text to tag for default
        * Set text for etree element (To match line_edits in window)
        """

        for tag in self.line_tags:
            etree.SubElement(element, tag).text = tag
        element = self.inventory[self]
        self.set_field_text()
        self.set_element_text(element)

    def set_field_text(self):
        """
        * Set element to value for key self in instance var inventory
        * Iterate over children in element (etree Element)
        * Get line_edit using instance var fieldDict
        """

        element = self.inventory[self]
        for child in element:
            if child.tag == 'Name':
                continue
            field = self.fieldDict[child.tag]
            if child.text is None:
                field.clear()
            else:
                field.setText(child.text)
        self.set_missing_tag_text(element)

    def set_element_text(self, element):
        """
        * Set element to value for key self in instance var inventory
        * Iterate over each tag in element (etree Element)
        * Try to set text for tag if tag is not an empty string
        * Pass if a KeyError occurs
        """
        removable_tags = [
            'Unlock',
            'Server',
            'Category',
            'NameGenerator'
        ]
        for child in element:
            field = self.fieldDict[child.tag]
            text = str(field.text())
            if child.tag == 'Name':
                continue
            if text:
                child.text = text
            else:
                if child.tag in removable_tags:
                    child.getparent().remove(child)
                else:
                    text = '' if child.tag == 'Description' else '1'
                    child.text = text
        self.check_missing_tags(element)

    def check_missing_tags(self, element):

        for tag in self.check_tags:
            field = self.fieldDict[tag]
            text = str(field.text())
            if text and element.find(tag) is None:
                etree.SubElement(element, tag).text = text

    def set_missing_tag_text(self, element):
        for tag in self.check_tags:
            if element.find(tag) is None:
                field = self.fieldDict[tag]
                field.clear()
