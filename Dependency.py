from lxml import etree


class Dependency:
    def __init__(self, parent, software, feature, scan=False):
        self.software = software
        self.feature = feature
        if not scan:
            self.create_dependency(parent, software, feature)

    @classmethod
    def delete_dependency(cls, feature, dependency_feature):
        """
        * Parameter: feature (etree Element)
        * Parameter:  dependency_feature (Dependency Object)
        * Find etree element with tag 'Dependency' with wanted text
        * Remove the dependency from its parent (An etree Element)
        """

        for child in feature:
            if child.tag == 'Dependency' and child.text == dependency_feature:
                feature.remove(child)


    def create_dependency(self, parent, software, feature):
        """
        * Parameter: parent (etree element of tag 'Feature')
        * Parameter: software (str)
        * Parameter: feature (str)
        * Create an etree subElement with a Tag "Dependency",
        * an attribute of Software equal to the parameter software
        * Text is set to the parameter feature (str)
        * Return element
        """

        dependency = etree.SubElement(parent, "Dependency", Software=software).text = feature
        return dependency