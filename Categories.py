from lxml import etree
from softwareModClasses import Category


class Categories:
    category_list = []

    def __init__(self, parent, combobox, scan):
        self.parent = parent
        self.combobox = combobox
        # Add category to root if not scan
        if not scan and parent.find('Categories') is None:
            parent.insert(5, etree.Element("Categories"))
        self.categories = parent.find('Categories')

    @classmethod
    def add(cls, parent, combobox, scan=False):
        return cls(parent, combobox, scan)

    @classmethod
    def clear_inventory(cls):
        """
        * Clear class variable (list) category_list
        """

        cls.category_list.clear()

    @classmethod
    def find_category(cls, name):
        """
        * Parameter: name (str)
        * Compare the instance variable name of each category in the
        * class list category_list
        * Return the category that passes the comparison.
        """

        for category in cls.category_list:
            if category.name == name:
                return category

    def delete(self):
        """
        * Clear combobox
        * Clear class list category_list
        * Remove categories (Etree Element) from self.parent (Etree Root)
        """

        self.combobox.clear()
        Categories.clear_inventory()
        self.parent.remove(self.categories)

    def add_category(self, name, scan=False):
        """
        * Parameter: name (str)
        * Add name to self.combobox
        * Create a Category object named after the parameter name
        * Append category object to category_list
        *
        * Note: To make it simple to scan categories from already
        * made files, multiple category objects with the same
        * values can be made, however, the cls method find_category
        * will only return the first value it finds and lists keep
        * order; therefore it will not affect the program. Also the
        * class object does not allow the same category to be added
        * to combo boxes or tree objects more than once.
        """

        if scan:
            category = Category.add(self.categories, name, self.combobox, True)
            self.category_list.append(category)
        else:
            category = Category.add(self.categories, name, self.combobox)
            self.category_list.append(category)

    def delete_category(self, category):
        """
        * Parameter: category (Category class object)
        * Execute category's delete method
        *
        * Note: Due to the chance of multiple category objects with the
        * same name existing in category list,these duplicates will not
        * be an issue until the original is erased, because they do not
        * behave as desired. This is due to not being added in the
        * etree. All objects with a name value equal to the value of the
        * name instance variable found in parameter category are deleted.
        """

        self.category_list.remove(category)
        category.delete()
        for category_object in self.category_list:
            if category_object.name == category.name:
                self.category_list.remove(category)
