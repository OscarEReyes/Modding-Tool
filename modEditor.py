import softwareModClasses as modClasses
from lxml import etree
from scanner import scan


def parse_tree(file_name):
    """
    * Open the given file, and parse it with etree.
    * Return an etree element.
    """

    try:
        with open(file_name) as f:
            parser = etree.XMLParser(remove_blank_text=True)
            return etree.parse(f, parser)
    except etree.XMLSyntaxError:
        pass


def get_removable_fields(window):
    removable_fields = {
        window.unlock: 'Unlock',
        window.retention: 'Retention',
        window.iterative: 'Iterative',
        window.popularity: 'Popularity'
    }

    return removable_fields


def get_forced_s_line_fields(window):
    s_vital_fields = {
        window.nameField: 'Name',
        window.category: 'Category',
        window.description: 'Description',
        window.random: 'Random',
        window.OS_Specific: 'OSSpecific',
        window.InHouse: 'InHouse',
    }

    return s_vital_fields


def set_software_tags(window):
    """
    * Parameter: window (QtMainWindow)
    * Set root fields.
    * Look for tag in window.tree (xml tree) and set text to var text
    """

    set_vital_s_line_tags(window)
    set_non_vital_tags(window)
    set_name_generator(window)
    check_for_lost_tags(window)


def set_vital_s_line_tags(window):
    """
    * Sets necessary software fields.
    """

    fields = get_forced_s_line_fields(window)

    for field, tag in fields.items():
        if tag == 'OSSpecific' or tag == 'InHouse':
            if field.isChecked():
                text = 'True'
            else:
                text = 'False'
        else:
            text = str(field.text())
            if not text:
                text = '1' if tag == 'Random' else tag
        window.tree.find(tag).text = text

    oss = True if window.tree.find('OSSpecific').text == 'True' else False
    set_os_limit(window, oss)


def set_non_vital_tags(window):
    """
    * Sets non_vital fields (Not necessary when categories are made)
    * Handles potential annoyances like tags that are not used existing
    """

    fields = get_removable_fields(window)
    tree = window.tree
    for line_edit, tag in fields.items():
        text = str(line_edit.text())
        child = tree.find(tag)
        root = tree.getroot()
        if tag == 'Unlock' and not text:
            remove_tag(root, child)
        elif tag == 'Unlock' and text:
            set_tag_text(root, child, tag, text)
        else:
            if window.categories is not None:
                remove_tag(root, child)


def set_name_generator(window):

    categories = window.categories
    line_edit = window.nameGenerator
    text = str(line_edit.text())
    tree = window.tree

    if not text and categories is None:
        text = str(window.nameField.text()) + 'NameGenerator'
    elif not text:
        text = ''
    set_tag_text(tree.getroot(), tree.find('NameGenerator'), 'NameGenerator', text)


def check_for_lost_tags(window):
    erasable_list = [
        'Iterative',
        'Popularity',
        'Retention'
    ]
    field_list = [
        window.iterative,
        window.popularity,
        window.retention
    ]
    tree = window.tree
    for i, tag in enumerate(erasable_list):
        element = tree.find(tag)
        text = str(field_list[i].text())
        if window.categories is None and element is None:
            if not text:
                text = '1'
            tree.getroot().insert(8 + i, etree.Element(tag))
            tree.find(tag).text = text


def set_tag_text(root, child, tag, text):
    if child is None:
        child = etree.SubElement(root, tag)
        child.text = text
    else:
        child.text = text


def remove_tag(root, child):
    if child is not None:
        root.remove(child)


def set_os_limit(window, os_specific):
    tag = window.tree.find('OSLimit')
    text = str(window.OSLimit.text())
    root = window.tree.getroot()

    if not os_specific and tag is not None:
        root.remove(tag)
    if os_specific and tag is not None and not text:
        root.remove(tag)
    if os_specific and tag is None and text:
        tag = etree.SubElement(root, 'OSLimit')
        tag.text = text
    if os_specific and tag is not None and text:
        tag.text = text


def set_main_fields(window):
    """
    * Parameter: window (QtMainWindow)
    * Get software_fields (dict) from method get_s_line_fields
    * Iterate over each Qt Line Edit object and etree tag in
    * software_fields
    * Look for tag in window.tree (xml tree) and store text in var text
    * Set line_edit current text to var value
    """

    set_vital_fields(window)
    set_non_vital_fields(window)
    set_name_generator_field(window)

    tag = window.tree.find('OSLimit')
    if tag is not None:
        window.OSLimit.setText(tag.text)


def set_non_vital_fields(window):
    tree = window.tree
    fields = get_removable_fields(window)
    for field, tag in fields.items():
        child = tree.find(tag)
        if child is not None:
            field.setText(child.text)
        else:
            field.clear()


def set_name_generator_field(window):
    tag = window.tree.find('NameGenerator')
    if tag is not None:
        if not tag.text:
            window.nameGenerator.clear()
        else:
            window.nameGenerator.setText(tag.text)


def set_vital_fields(window):
    tree = window.tree
    fields = get_forced_s_line_fields(window)
    for field, tag in fields.items():
        child = tree.find(tag)
        if tag == 'OSSpecific' or tag == 'InHouse':
            states = {
                'True': True,
                'False': False
            }
            field.setCheckState(states[child.text])
        else:
            field.setText(child.text)


def find_feature(window):
    """
    * Parameter: window (Qt mainWindow Object)
    * Try to:
    * Get current text of feature_box (Qt Combobox) & store it in var
    * Use Feature class function find_by_name to find Feature object
    * Store it in window's instance var feature.
    * Display message if no features are found. (Causes IndexError)
    """

    try:
        name = str(window.feature_box.currentText())
        feature = modClasses.Feature.find_by_name(name)
        return feature

    except IndexError:
        window.statusBar().showMessage('No features found', 1500)


def update_category_fields(window, status):
    """
    * Set fields in fields (list) to parameter status
    """

    fields = [
        window.removeCategoryButton,
        window.addCategoryButton,
        window.category_box
    ]
    for field in fields:
        field.setEnabled(status)


def set_categories_status(window):
    """
    * Parameter: window (Qt mainWindow object)
    * Check for Categories tag in window.tree
    * Enable category_check_box if Categories tag exists.
    """

    if window.tree.find('Categories') is None:
        categories_status = False
    else:
        categories_status = True
    window.categoryCheckbox.setChecked(categories_status)


def extract_data(window):
    """
    * Parameter: window (Qt mainWindow object)
    * Execute method set_categories_status
    * Execute method find_feature
    * Execute method set_main_fields
    """

    scan(window.tree, window.category_box, window.feature_box)
    window.load_category()
    set_categories_status(window)
    find_feature(window)
    set_main_fields(window)
