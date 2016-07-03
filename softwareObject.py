
class SoftwareObject:
    inventory = {}
    line_tags = []

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    @classmethod
    def find_by_name(cls, name):
        for Object in cls.inventory:
            if Object.name == name:
                return Object

    @classmethod
    def set_field_dicts(cls, line_fields):
        cls.fieldDict = dict(zip(cls.line_tags, line_fields))

    def delete(self, combobox):
        self.inventory.pop(self)
        self.remove_from_combobox(combobox)
        self.remove_from_tree()

    @staticmethod
    def remove_from_combobox(combobox):
        current_index = combobox.currentIndex()
        combobox.removeItem(current_index)

    def remove_from_tree(self):
        instance = self.inventory[self]
        self.parent.remove(instance)

    def set_line_field_text(self):

        element = self.inventory[self]
        for child in element.iter():
            line_edit = self.fieldDict[child.tag]
            line_edit.setText(child.text)

    def set_etree_element_text(self):

        element = self.inventory[self]
        for child in element.iter():
            text = str(self.fieldDict[child.tag].text())
            if text:
                child.text = text
