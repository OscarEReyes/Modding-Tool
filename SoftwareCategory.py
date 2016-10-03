from lxml import etree


class SoftwareCategory:
    def __init__(self, parent, category, unlock, scan=False):
        self.software = category
        self.feature = unlock
        if not scan:
            self.create_software_category(parent, category, unlock)

    @classmethod
    def delete_category(cls, feature, software_category):
        """
        * Parameter: feature (etree element -Tag- 'Feature')
        * Parameter: software_category (SoftwareCategory Object)
        * Remove the dependency from feature (etree element)
        """

        for child in feature:
            if child.tag == 'SoftwareCategory' and child.text == software_category:
                feature.remove(child)
                break

    def create_software_category(self, parent, category, unlock):
        """
        * Parameter: parent (etree element -Tag- 'Feature')
        * Parameter: category (str)
        * Parameter: unlock (str)
        * Create an etree subElement with a Tag "SoftwareCategory",
        * an attribute of Software equal to the parameter category.
        * Set text to the unlock parameter value
        * Return etree element
        """
        etree.SubElement(parent, "SoftwareCategory", Category=category).text = unlock
