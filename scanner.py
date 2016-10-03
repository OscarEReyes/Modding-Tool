from softwareModClasses import Feature
from Categories import Categories
line_tags = [
    'Name',
    'Description',
    'Unlock',
    'NameGenerator',
    'Popularity',
    'TimeScale',
    'Retention',
    'Iterative'
]


def scan(tree, c_combo_box, f_combo_box):
    """
    * Parameter: tree (etree root element)
    * Parameter: c_combo_box (Qt combobox object)
    * Parameter: f_combo_box  (Qt combobox object)
    * Look for 'Categories tag in tree, store it, and
    * If it is not None execute look_for_categories method
    *
    * Look for 'Features' tag in tree and store it
    * Execute look_for_features method
    """

    categories = tree.find('Categories')
    if categories is not None:
        search_categories(categories, c_combo_box)

    features = tree.find('Features')
    search_features(features, f_combo_box)


def search_categories(categories, combobox):
    """
    * Parameter: categories  (etree element -Tag- 'Categories)
    * Parameter: combobox (Qt Combobox object)
    * Create Categories object -Note- Pass opt parameter Scan as True
    * Iterate over category (etree element tag 'Category) in categories
    * Get name of category (attrib 'Name')
    * Execute add_category method for each category (Category Object)
    """

    categories_object = Categories.add(categories.getparent(), combobox, True)
    for category in categories:
        name = category.attrib["Name"]
        categories_object.add_category(name, True)


def search_features(features, combobox):
    """
    * Parameter: features (etree element -Tag- 'Features')
    * Iterate over feature elements (etree elements) in features
    * Look for tag 'Name' in feature and store its text in var name
    * Create Feature Object for each feature
    * Execute look_for_dependencies method for each Feature Object
    """

    for feature in features:
        name = feature.find('Name').text
        f = Feature.add(features, name, combobox, True)
        search_dep(feature, f)
        search_soft_categ(feature, f)


def search_dep(feature, f):
    """
    * Parameter: feature (etree Element -Tag- 'Feature')
    * Parameter: f (Feature object)
    * Iterate over feature's elements (etree elements)
    * Look for tag 'Dependency' in feature and store its text in var
    * Get element attribute 'Software' and store it in a var
    * Add dependency object to f
    """

    for element in feature:
        if element.tag == 'Dependency':
            dependency = element.text
            software = element.attrib["Software"]
            f.scan_special_tag('f', software, dependency)


def search_soft_categ(feature, f):
    """
    * Parameter: feature(etree Element -Tag- 'Feature')
    * Parameter: f (Feature object)
    * Iterate over feature's elements (etree elements)
    * Look for tag 'Dependency' in feature and store its text in var
    * Get element attribute 'Software' and store it in a var
    * Add dependency object to f
    """

    for attribute in feature:
        if attribute.tag == 'SoftwareCategory':
            unlock = attribute.text
            category = attribute.attrib["Category"]
            f.scan_software_category('sc', category, unlock)
