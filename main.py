import sys
from os import path
from lxml import etree
from PyQt4 import QtGui
import design
import modCreator as modCreator
import softwareModClasses as modClasses
import scanner


class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
        self.setupUi(self)
        self.openButton.clicked.connect(self.open_file_handler)
        self.saveButton.clicked.connect(lambda: self.save())
        self.newModButton.clicked.connect(self.create_mod)
        self.saveSoftwareButton.clicked.connect(self.update_software_fields)

        # Feature Buttons #
        self.savechanges.clicked.connect(self.update_feature)
        self.renameFeatureButton.clicked.connect(self.rename_feature)
        self.addFeatureButton.clicked.connect(self.add_feature)
        self.deleteFeatureButton.clicked.connect(self.delete_feature)

        # Category Buttons #
        self.saveCategoryChanges.clicked.connect(self.update_category)
        self.addCategoryButton.clicked.connect(self.add_category)
        self.removeCategoryButton.clicked.connect(self.delete_category)

        # Dependency buttons #
        self.addDependencyButton.clicked.connect(self.add_dependency)

        # State Change functions. #
        self.fComboBox.activated.connect(self.load_feature)
        self.cComboBox.activated.connect(self.load_category)
        self.categoryCheckbox.stateChanged.connect(self.check_categories)
        self.fLineFields = [
            self.fDesc,
            self.featureUnlock,
            self.featureDevTime,
            self.featureInnovation,
            self.featureUsability,
            self.featureStability,
            self.featureCodeArt,
            self.featureServer
        ]
        self.cLineFields = [
            self.category_description,
            self.category_unlock,
            self.category_popularity,
            self.category_retention,
            self.category_time_scale,
            self.category_iterative,
            self.c_name_generator
        ]
        self.sLineFields = {
            self.nameField: 'Name',
            self.category: 'Category',
            self.description: 'Description',
            self.unlock: 'Unlock',
            self.osSpecific: 'OSSpecific',
            self.inHouse: 'InHouse',
            self.nameGenerator: 'NameGenerator',
            self.random: 'Random',
            self.retention: 'Retention',
            self.iterative: 'Iterative',
            self.population: 'Population'
        }
        modClasses.Feature.set_field_dicts(self.fLineFields)
        modClasses.Category.set_field_dicts(self.cLineFields)

        # self.fComboBox.currentIndexChanged.connect(self.rename_feature)
        main_menu = self.menuBar()
        file_menu = self.add_menu_to_menu_bar(main_menu, '&File')
        self.define_action(file_menu, "&Close", "Ctrl+Q", self.close)
        self.define_action(file_menu, "&Save As", "", self.save_as)
        self.define_action(file_menu, "&Save", "Ctrl+S", self.save)
        self.define_action(file_menu, "&New Mod", "Ctrl+N", self.create_mod)
        self.dialog = QtGui.QFileDialog()

    @staticmethod
    def add_menu_to_menu_bar(menu, name):
        return menu.addMenu(name)

    @staticmethod
    def add_menu_bar_action(file_menu, action):
        file_menu.addAction(action)

    def define_action(self, file_menu, action_name, shortcut, function):
        action = QtGui.QAction(action_name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function)
        self.add_menu_bar_action(file_menu, action)

    def close(self):
        message = 'Unsaved progress will be lost.\nDo you wish to continue?'
        choice = QtGui.QMessageBox.question(self, "Warning", message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()

    def get_file_name(self, type):
        """ Prompts the user for a file_name """

        if type == 'save':
            file_name = QtGui.QFileDialog.getSaveFileName(self.dialog, 'Save', '', '*.xml')
        elif type == 'saveAs':
            file_name = QtGui.QFileDialog.getSaveFileName(self.dialog, 'Save As', '', '*.xml')
        else:
            file_name = QtGui.QFileDialog.getOpenFileName(self.dialog, 'Open File', '', '*.xml')
        return file_name

    def create_mod(self):
        """ Creates an xml file with the required fields. """

        file_name = self.get_file_name('save')
        feature_num = self.featureNum.value()
        modCreator.create_mod(feature_num, file_name, self.fComboBox)

        self.open_file(file_name)
        self.statusBar().showMessage('New Mod Created', 1500)

    def open_file_handler(self):
        """ Gets a file_name and creates an instance variable
            for the current directory, then opens the file. """

        file_name = self.get_file_name('open')
        self.directory = path.dirname(file_name)
        self.open_file(file_name)

    def open_file(self, file_name):
        """ Opens and parses xml file. """

        try:
            self.file_name = file_name
            self.tree = self.parse_tree(file_name)
            self.extract_data()
            self.statusBar().showMessage('File Opened', 1500)
        except FileNotFoundError:
            pass

    def parse_tree(self, file_name):
        """ Opens the given file, and parses it with etree.
            Returns an etree element. """

        with open(file_name) as f:
            parser = etree.XMLParser(remove_blank_text=True)
            return etree.parse(f, parser)

    def extract_data(self):
        scanner.scan(self.tree, self.fComboBox, self.dComboBox)
        self.set_categories_status()
        self.find_feature()
        self.set_main_fields()

    def set_main_fields(self):
        """ Sets the text for the fields in sLineFields"""

        for line_edit, tag in self.sLineFields.items():
            value = str(self.tree.find(tag).text)
            line_edit.setText(value)

    def set_categories_status(self):
        """ Checks for Categories tag in self.tree
            and enables category_check_box if it exists."""

        if self.tree.find('Categories') is None:
            categories_status = False
        else:
            categories_status = True
        self.categoryCheckbox.setCheckState(categories_status)

    def save(self):
        """ Saves the file to current directory."""

        try:
            with open(self.file_name, 'wb+') as f:
                self.tree.write(f, pretty_print=True)
            self.statusBar().showMessage('Saved', 1500)
        except AttributeError:
            self.statusBar().showMessage('Error, no file opened or created', 1500)

    def save_as(self):
        """ Save As Function. Allows new file_name and new directory """

        try:
            self.file_name = self.get_file_name('saveAs')
            self.directory = QtGui.QFileDialog.getExistingDirectory(self.dialog, 'Save As')
            self.save()
        except FileNotFoundError:
             self.statusBar().showMessage('Failed to Save', 1500)

    def load_category(self):
        """ Loads currently selected category from category combobox"""

        name = str(self.cComboBox.currentText())
        self.category = modClasses.Category.find_by_name(name)
        self.category.set_line_field_text()

    def check_categories(self):
        """ Checks if the categories checkbox is selected
            * Adds categories object if it is checked
            * Deletes Categories object if it is not checked
            * Updates category fields. """

        try:
            status = self.categoryCheckbox.isChecked()
            if status:
                root = self.tree.getroot()
                self.categories = modClasses.Categories.add(root, self.cComboBox)
            else:
                self.categories.delete()
            self.update_category_fields(status)
        except AttributeError:
            self.statusBar().showMessage('No file selected.', 1500)

    def update_category_fields(self, status):
        """ Update category fields to status parameter """

        fields = [
            self.removeCategoryButton,
            self.addCategoryButton,
            self.cComboBox
        ]
        for field in fields:
            field.setEnabled(status)

    def add_category(self):
        """ Add new Category object """

        name = str(self.category_name.text())
        if name:
            self.categories.add_category(name)

    def update_category(self):
        """ Applies changes to currently selected category and then repopulates
            its fields on the mainWindow"""

        try:
            self.category.set_etree_element_text()
        except AttributeError:
            self.statusBar().showMessage('Error. Open or create a mod.', 1500)

    def delete_category(self):
        """ Deletes currently selected category object"""

        self.categories.delete_category(self.category)

    def find_feature(self):
        """ Uses the Feature class function find_by_name to find the Feature
            object and store it in an instance variable. """

        try:
            name = str(self.fComboBox.currentText())
            self.feature = modClasses.Feature.find_by_name(name)
        except IndexError:
            self.statusBar().showMessage('No features found', 1500)

    def load_feature(self):
        """ Finds the currently selected feature and loads the GUI's fields
            to match the feature's values """

        self.find_feature()
        self.feature.set_line_field_text()

    def update_software_fields(self):
        """ Sets the tag text for each tag in software. """

        try:
            self.set_software_tags()
            self.statusBar().showMessage('Changes made', 1500)
        except AttributeError:
            self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def set_software_tags(self):
        """ Sets the text for the tags in sLineFields"""

        for line_edit, tag in self.sLineFields.items():
            value = str(line_edit.text())
            self.tree.find(tag).text = value

    def update_feature(self):
        """ Updates attributes and etree_element_text
            for currently selected feature """

        attributes = {
            'Vital': self.vitalCheckBox.isChecked(),
            'Forced': self.forcedCheckbox.isChecked(),
            'From': self.FROMCHECKBOX.isChecked()
        }
        from_text = str(self.fromEdit.text())
        try:
            self.feature.set_etree_element_text()
            self.feature.check_attribute(attributes, from_text)
        except AttributeError:
            self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def rename_feature(self):
        """ Renames currently selected feature"""

        name = str(self.newNameEdit.text())
        if name:
            self.feature.rename(name)

    def add_feature(self):
        """ Adds feature to tree"""

        name = str(self.featureNameEdit.text())
        features = self.tree.find('Features')
        if name:
            modClasses.Feature.add(features, name, self.fComboBox)

    def delete_feature(self):
        """ Deletes currently selected feature"""

        feature_name = str(self.fComboBox.currentText())
        if feature_name:
            self.feature.delete(self.feature.combobox)

    def add_dependency(self):
        """ Creates dependency object for self.feature
            Takes in the variables dependency_feature and software """

        try:
            dependency_feature = str(self.dependency_feature.text())
            software = str(self.dependency_software.text())
            self.feature.add_dependency(software, dependency_feature)
        except NameError:
            self.statusBar().showMessage('Error adding dependency', 1750)


def main():
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
