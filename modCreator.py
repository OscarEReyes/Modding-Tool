from lxml import etree
import softwareModClasses as modClasses


def create_mod(spinbox, mod_name, combobox):
    """
    * Create an etree Element. (The root of the xml tree)
    * Create the expected tags. (Executes create_tags method)
    * Add features (The number depending form user input)
    * Save move to parameter mod_name (name for file)
    """

    root = etree.Element("SoftwareType")
    create_tags(root)
    number_of_features = spinbox.value()
    add_features(root, number_of_features, combobox)
    save_mod(root, mod_name)


def create_tags(root):
    """
    * Parameter: root (etree element)
    * Create a subElement in root for each field in field_list (list)
    """

    field_list = [
        'Name',
        'Category',
        'Description',
        'Unlock',
        'OSSpecific',
        'InHouse',
        'NameGenerator',
        'Random',
        'Retention',
        'Iterative',
        'Popularity'
    ]

    for field in field_list:
        if field == 'OSSpecific' or field == 'InHouse':
            text = 'False'
        elif field == 'Retention' or field == 'Popularity' or field == 'Iterative':
            text = '1'
        else:
            text = field
        etree.SubElement(root, field).text = text

def add_features(root, number_of_features, combobox):
    """
    * Parameter: root (etree element)
    * Create subElement in root with the tag 'Features'
    * Iterate over number_of_features (int)
    * Create a Feature element each time
    * (Will also create etree element)
    """

    features = etree.SubElement(root, "Features")
    for num in range(number_of_features):
        name = 'Feature {}'.format(num + 1)
        modClasses.Feature.add(features, name, combobox)


def save_mod(root, name):
    """
    * Parameter: root (etree element)
    * Parameter: name (str)
    * Turn etree to string (with pretty_print) and store it in a var
    * Write in file named after parameter name
    * (Create file if not existent)
    """

    try:
        file_to_save = (etree.tostring(root, pretty_print=True))
        with open(name, 'wb+') as f:
            f.write(file_to_save)
    except FileNotFoundError:
        pass
