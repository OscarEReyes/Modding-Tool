import softwareModClasses as sMC

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


def scan(tree, combobox1, combobox2):
    root = tree.getroot()

    categories = tree.find('Categories')
    if categories is not None:
        look_for_categories_tag(categories, combobox1)

    category = tree.find('Category')
    if category is not None:
        look_for_category(category, root)

    features = tree.find('Features')
    look_for_features(features, combobox2)


def look_for_features(features, combobox2):
    for feature in features:
        name = feature.find('Name').text
        f = sMC.Feature.add(features, name, combobox2)
        look_for_dependencies(feature, f)


def look_for_dependencies(feature, f):
    for attribute in feature:
        if attribute.tag == 'Dependency':
            dependency = attribute.text
            software = attribute.attrib["Software"]
            f.add_dependency(software, dependency)


def look_for_category(category, root):

        name = category.find('Name').text
        current_category = sMC.Category.add(root, name, True, True)
        sMC.Category.inventory[current_category] = category


def look_for_categories_tag(categories, combobox):

        categories_object = sMC.Categories.add(categories.getparent(), combobox, True)
        for category in categories:
            name = category.find('Name').text
            categories_object.scan_category(name)



