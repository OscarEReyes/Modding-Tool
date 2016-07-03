from lxml import etree
import softwareModClasses as smc 


def create_mod(number_of_features, mod_name, combobox):
    root = etree.Element("SoftwareType")
    create_tags(root)
    add_features(root, number_of_features, combobox)
    save_mod(root, mod_name)


def create_tags(root):
    field_list = [
        'Name',
        'Description',
        'Unlock',
        'OSSpecific',
        'InHouse',
        'NameGenerator',
        'Random',
        'Iterative',
        'Retention',
        'Population'
        ]

    for field in field_list:
        etree.SubElement(root, field).text = field
    smc.Category.add(root, None, True)


def add_features(root, number_of_features, combobox):
    features = etree.SubElement(root, "Features")
    for num in range(number_of_features):
        name = 'Feature {}'.format(num + 1)
        smc.Feature.add(features, name, combobox)


def save_mod(root, name):
    try:
        file_to_save = (etree.tostring(root, pretty_print=True))
        with open(name, 'wb+') as f:
            f.write(file_to_save)
    except FileNotFoundError:
        pass


def set_tag_text(parent, line_fields, category_field):
    if parent.find('Category') is not None:
        parent.find('Category').text = category_field.text()

    for lineEdit, tag in line_fields.items():
        value = str(lineEdit.text())
        parent.find(tag).text = value


def set_field_text(parent, line_fields, category_field):
    if parent.find('Category') is not None:
        value = str(parent.find('Category').text)
        category_field.setText(value)
    else:
        category_field.setText('Edit Category from Categories')

    for lineEdit, category in line_fields.items():
        value = str(parent.find(category).text)
        lineEdit.setText(value)
