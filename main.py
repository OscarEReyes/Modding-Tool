import sys
from os import path
from lxml import etree
from PyQt4 import QtGui
import design
import modCreator as mc
import softwareModClasses as smc
import scanner


# import errorMessages as em

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
            self.categName,
            self.categDesc,
            self.categUnlock,
            self.categPopularity,
            self.categRetention,
            self.categTimeScale,
            self.categIterative,
            self.categNameGen
        ]
        self.sLineFields = {
            self.nameField: 'Name',
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
        smc.Feature.set_field_dicts(self.fLineFields)
        smc.Category.set_field_dicts(self.cLineFields)
        # self.fComboBox.currentIndexChanged.connect(self.rename_feature)
        main_menu = self.menuBar()
        file_menu = self.add_menu_to_menu_bar(main_menu, '&File')
        self.define_action(file_menu, "&Close", "Ctrl+Q", self.close)
        self.define_action(file_menu, "&Save As", "", self.save_as)
        self.define_action(file_menu, "&Save", "Ctrl+S", self.save)
        self.define_action(file_menu, "&New Mod", "Ctrl+N", self.create_mod)
    @staticmethod
    def add_menu_to_menu_bar(menu, name):
        return menu.addMenu(name)

    def add_menubar_action(self, file_menu, action):
        file_menu.addAction(action)

    def define_action(self, fileMenu, actionName, shortcut, function):
        action = QtGui.QAction(actionName, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function)
        self.add_menubar_action(fileMenu, action)

    def close(self):
        message = ('All unsaved progress will be lost.Do you wish to continue?')
        choice = QtGui.QMessageBox.question(self, "Warning", message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()

    def create_mod(self):
        """ Creates an xml file with the required fields. """

        self.fileName = QtGui.QFileDialog.getSaveFileName(self, 'Choose a name for your mod')
        mc.create_mod(self.featureNum.value(), self.fileName, self.fComboBox)
        self.open_file(self.fileName)

        self.statusBar().showMessage('New Mod Created', 1500)

    def open_file_handler(self):
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        self.directory = path.dirname(self.fileName)
        self.open_file(self.fileName)

    def open_file(self, file_name):
        """ Opens and parses an xml file. Enables buttons & fields"""

        try:
            with open(file_name) as f:
                parser = etree.XMLParser(remove_blank_text=True)
                self.tree = etree.parse(f, parser)

            self.extract_info()
            mc.set_field_text(self.tree, self.sLineFields, self.categoryField)

            self.statusBar().showMessage('File Opened', 1500)
        except FileNotFoundError:
            pass

    def extract_info(self):
        scanner.scan(self.tree, self.fComboBox, self.dComboBox)
        self.handle_categories()
        self.find_feature()

    def save(self):
        """ Saves the file to current directory."""
        try:
            with open(self.fileName, 'wb+') as f:
                self.tree.write(f, pretty_print=True)
            self.statusBar().showMessage('Saved', 1500)
        except AttributeError:
            self.statusBar().showMessage('Error, no file opened or created', 1500)

    def save_as(self):
        """ Save As Function. Self-explanatory"""

        try:
            self.fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save As')
            self.directory = QtGui.QFileDialog.getExistingDirectory(self, 'Choose your directory')
            self.save()
            with open(self.directory, 'w') as directory:
                directory.write(path.basename(path.normpath(self.fileName)))
        except FileNotFoundError:
            self.statusBar().showMessage('Failed to Save', 1500)

    def handle_categories(self):
        """ Populates the appropriate text fields in the GUI. """

        categories_status = False if self.tree.find('Categories') is None else True
        if not categories_status:
            self.category = smc.Category.return_single_category()
            self.category.category.set_line_field_text()
        self.categoryCheckbox.setCheckState(categories_status)

    def load_category(self):
        name = str(self.cComboBox.currentText())
        self.category = smc.Category.find_by_name(name)

    def check_categories(self):
        """ Checks if the categories checkbox is selected and performs
            the required actions. """
        try:
            status = self.categoryCheckbox.isChecked()
            if status:
                self.switch_to_categories()
            else:
                self.switch_to_category()
            self.update_category_fields(status)
        except AttributeError:
            self.statusBar().showMessage('No file selected.', 1500)

    def switch_to_categories(self):
        self.categories = smc.Categories.add(self.tree.getroot(), self.cComboBox)
        self.category.erase()

    def switch_to_category(self):
        self.categories.delete()
        name = str(self.categName.text())
        self.category = smc.Category.add(self.tree.getroot(), name, True)

    def update_category_fields(self, status):
        fields = [
            self.removeCategoryButton,
            self.addCategoryButton,
            self.cComboBox
        ]

        for field in fields:
            field.setEnabled(status)

    def add_category(self):

        name = str(self.categName.text())
        if name:
            self.categories.add_category(name)

    def update_category(self):
        """ Applies changes to currently selected category and then repopulates
            its fields on the mainWindow"""

        try:
            self.category.set_etree_element_text()
            self.category.set_line_field_text()
        except AttributeError:
            self.statusBar().showMessage('Error updating category. Open or create a mod.', 1500)

    def delete_category(self):
        """ Deletes currently selected category"""

        self.categories.delete_category(self.category)

    def find_feature(self):

        try:
            name = str(self.fComboBox.currentText())
            self.feature = smc.Feature.find_by_name(name)
        except IndexError:
            self.statusBar().showMessage('No features found', 1500)

    def update_software_fields(self):

        """ Sets the tag text for each tag in software. Removes the
            Categories tag if self.categStatus is False otherwise
            it assigns the appropriate text to each tag """

        try:
            mc.set_tag_text(self.tree, self.sLineFields, self.categoryField)
            self.statusBar().showMessage('Changes made', 1500)
        except AttributeError:
            self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def load_feature(self):
        self.find_feature()
        self.feature.set_line_field_text()

    def update_feature(self):
        attribs = {
            'Vital': self.vitalCheckBox.isChecked(),
            'Forced': self.forcedCheckbox.isChecked(),
            'From': self.FROMCHECKBOX.isChecked()
        }

        from_text = str(self.fromEdit.text())
        try:
            self.feature.set_etree_element_text()
            self.feature.check_attribute(attribs, from_text)
        except AttributeError:
            self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def rename_feature(self):
        """ Renames currently selected feature"""

        name = str(self.newNameEdit.text())
        if name:
            self.feature.rename(name)

    def add_feature(self):
        """ Adds feature"""

        name = str(self.featureNameEdit.text())
        features = self.tree.find('Features')
        if name:
            smc.Feature.add(features, name, self.fComboBox)

    def delete_feature(self):
        """ Deletes currently selected feature"""

        feature_name = str(self.fComboBox.currentText())
        if feature_name:
            self.feature.delete(self.feature.combobox)

    def add_dependency(self):
        try:
            feature = str(self.dependency_feature.text())
            software = str(self.dependency_software.text())
            self.feature.add_dependency(software, feature)
        except NameError:
            self.statusBar().showMessage('Error adding dependency', 1750)


def main():
    app = QtGui.QApplication(sys.argv)
    global form
    form = MainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
