import sys
from os import path
from PyQt4 import QtGui
import design
from modEditor import *
from modCreator import create_mod
from softwareModClasses import *
import qdarkstyle
from Categories import Categories
from genericThread import *
from threads import *


class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.set_up_buttons(self)
        self.set_feature_buttons(self)
        self.set_category_buttons(self)
        self.connect_state_changes(self)

        self.fLineFields = [
            self.feature_category,
            self.feature_description,
            self.feature_unlock,
            self.feature_dev_time,
            self.feature_innovation,
            self.feature_usability,
            self.feature_stability,
            self.feature_code_art,
            self.feature_server
        ]
        self.cLineFields = [
            self.category_description,
            self.category_unlock,
            self.category_popularity,
            self.category_retention,
            self.category_time_scale,
            self.category_iterative,
            self.category_name_generator
        ]
        Feature.set_field_dicts(self.fLineFields)
        Category.set_field_dicts(self.cLineFields)
        self.define_actions(self)
        self.dialog = QtGui.QFileDialog()
        self.categories = None
        self.threadPool = []

    @staticmethod
    def set_up_buttons(window):
        window.openButton.clicked.connect(window.open_file_handler)
        window.newModButton.clicked.connect(window.create_mod_handler)
        window.saveSoftwareButton.clicked.connect(window.update_software_fields)

    @staticmethod
    def set_feature_buttons(window):
        window.savechanges.clicked.connect(window.update_feature)
        window.renameFeatureButton.clicked.connect(window.rename_feature)
        window.addFeatureButton.clicked.connect(window.add_feature)
        window.deleteFeatureButton.clicked.connect(window.delete_feature)
        window.addDependencyButton.clicked.connect(window.add_dependency)
        window.add_software_category_button.clicked.connect(window.add_software_category)
        window.load_dependency_button.clicked.connect(window.load_dependency)
        window.load_category_button.clicked.connect(window.load_software_category)
        window.del_dep_button.clicked.connect(window.delete_dependency)
        window.del_categ_button.clicked.connect(window.delete_software_category)

    @staticmethod
    def set_category_buttons(window):
        window.saveCategoryChanges.clicked.connect(window.update_category)
        window.addCategoryButton.clicked.connect(window.add_category)
        window.removeCategoryButton.clicked.connect(window.delete_category)

    @staticmethod
    def connect_state_changes(window):
        window.feature_box.activated.connect(window.load_feature)
        window.category_box.activated.connect(window.load_category)
        window.categoryCheckbox.stateChanged.connect(window.check_categories)

    @staticmethod
    def define_actions(window):
        main_menu = window.menuBar()
        file_menu = window.add_menu_to_menu_bar(main_menu, '&File')

        window.define_action(file_menu, "&Close", "Ctrl+Q", window.close)
        window.define_action(file_menu, "&Save As", "", window.save_as)
        window.define_action(file_menu, "&Save", "Ctrl+S", window.save)
        window.define_action(file_menu, "&New Mod", "Ctrl+N", window.create_mod)

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

    def closeEvent(self, event):
        """
        * Override closeEvent method to ask user if he/she wishes
        * to exit
        """
        message = 'Unsaved progress will be lost.\nDo you wish to continue?'
        message_box = QtGui.QMessageBox()

        choice = QtGui.QMessageBox.question(message_box, "Warning",
                                            message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def get_file_name(self, save_type):
        """
        * Prompt the user for a file_name
        """

        if save_type == 'save':
            file_name = QtGui.QFileDialog.getSaveFileName(self.dialog, 'Save', '', '*.xml')
        elif save_type == 'saveAs':
            file_name = QtGui.QFileDialog.getSaveFileName(self.dialog, 'Save As', '', '*.xml')
        else:
            file_name = QtGui.QFileDialog.getOpenFileName(self.dialog, 'Open File', '', '*.xml')
        return file_name

    def create_mod(self):
        """
        * Create mod
        * Display message 'New Mod Created'
        """
        create_mod(self.featureNum, self.file_name, self.feature_box)
        self.statusBar().showMessage('New Mod Created', 1500)

    def create_mod_handler(self):
        """
        * Create an xml file with the required fields.
        """

        self.file_name = self.get_file_name('save')
        self.feature_num = self.featureNum.value()
        if self.file_name and self.feature_num:
            thread = WorkThread()
            self.connect(thread, QtCore.SIGNAL('create_mod()'), self.create_mod)
            thread.start()
            self.open_file()

    def open_file_handler(self):
        """
        * Get file_name
        * Set self.directory to current working directory
        * Open file
        """

        self.categories = None
        self.file_name = self.get_file_name('open')
        self.directory = path.dirname(self.file_name)
        combo_boxes = [
            self.feature_box,
            self.category_box,
            self.dependency_box,
            self.soft_category_box
        ]
        for box in combo_boxes:
            box.clear()
        self.open_file()

    def open_file(self):
        """
        * Open and parse xml file.
        """

        try:
            self.tree = parse_tree(self.file_name)
            extract_data(self)

            self.statusBar().showMessage('File Opened', 1500)
        except FileNotFoundError:
            pass

    def find_feature(self):
        """
        * Try to:
        * Get current text of feature_box (Qt Combobox) & store it in var
        * Use Feature class function find_by_name to find Feature object
        * Store it in window's instance var feature.
        * Display message if no features are found. (Causes IndexError)
        """

        try:
            name = str(self.feature_box.currentText())
            self.feature = Feature.find_by_name(name)
        except IndexError:
            self.statusBar().showMessage('No features found', 1500)

    def save(self):
        """
        * Saves the file to current directory.
        """

        try:
            with open(self.file_name, 'wb+') as f:
                self.tree.write(f, pretty_print=True)
            self.statusBar().showMessage('Saved', 1500)
        except AttributeError:
            self.statusBar().showMessage('Error, no file opened or created', 1500)

    def save_as(self):
        """
        * Save As Function. Allows new file_name and new directory
        * Get file_name
        * Get directory
        * Save
        """

        try:
            self.file_name = self.get_file_name('saveAs')
            self.directory = QtGui.QFileDialog.getExistingDirectory(self.dialog, 'Save As')
            self.save()
        except FileNotFoundError:
            self.statusBar().showMessage('Failed to Save', 1500)

    def load_category(self):
        """
        * Loads currently selected category from category combobox
        * Set name to self.category_box current text
        * Find_by_name and store result in var
        * Set line_field text
        """

        if self.category_box.count():
            name = str(self.category_box.currentText())
            self.c_category = Category.find_by_name(name)
            self.c_category.set_line_field_text()

    def check_categories(self):
        """
        * Check if the categories checkbox is selected
        * Add Categories object if it is checked
        * Delete Categories object if it is not checked
        * Update category fields
        * Display error message if AttributeError occurs
        """

        try:
            status = self.categoryCheckbox.isChecked()
            if status:
                root = self.tree.getroot()
                self.categories = Categories.add(root, self.category_box, False)
            else:
                self.categories.delete()
                self.categories = None
            set_software_tags(self)
            update_category_fields(self, status)
        except AttributeError:
            self.statusBar().showMessage('No file selected.', 1500)

    def add_category(self):
        """
        * Add new Category object
        * If name is not an empty string
        * Add category to self.categories
        """

        name = str(self.category_name.text())
        if name:
            self.categories.add_category(name)

    def update_category(self):
        """
        * Applies changes to currently selected category
        * then repopulates its fields on the mainWindow
        *
        * Try to execute self.category method set_etree_element_text
        * Set line field text
        * Display error message if AttributeError occurs.
        """

        try:
            if self.category_box.count():
                self.c_category.set_etree_element_text()
                self.c_category.set_line_field_text()
        except AttributeError:
            pass

    def delete_category(self):
        """
        * Deletes currently selected category object
        * Delete category
        """
        if self.category_box.count():
            self.categories.delete_category(self.c_category)
        if self.category_box.count():

            self.load_category()

    def load_feature(self):
        """
        * Finds the currently selected feature and loads field values
        * to GUI's fields
        *
        * Find Feature object and store it in self.feature
        * Set line field text
        """

        self.feature = find_feature(self)
        self.feature.set_line_field_text()
        self.load_dependencies()
        self.load_software_categories()
        self.load_feature_checkboxes()

    def load_feature_checkboxes(self):
        """
        * Check for attributes in feature
        * If attribute in feature.attrib, check box
        """

        attributes = {
            'Research': self.research_check_box,
            'Vital': self.vital_radio_button,
            'Forced': self.forced_radio_button,
            'From': self.from_radio_button
        }
        feature = Feature.inventory[self.feature]
        self.research_check_box.setChecked(False)
        self.none_radio_button.setChecked(True)
        for attribute, box in attributes.items():
            if attribute in feature.attrib:
                box.setChecked(True)

    def load_dependencies(self):
        """
        * Load dependencies to combobox
        """

        self.dependency_box.clear()
        feature = Feature.inventory[self.feature]
        for child in feature:
            if child.tag == 'Dependency':
                self.dependency_box.addItem(child.text)

    def load_software_categories(self):
        """
        * Load software categories to combobox
        """

        self.soft_category_box.clear()
        feature = Feature.inventory[self.feature]
        for child in feature:
            if child.tag == 'SoftwareCategory':
                self.soft_category_box.addItem()

    def load_dependency(self):
        """
        * Loads dependency
        """

        try:
            dependency_feature = self.dependency_box.currentText()
            dependency = self.feature.dependencies[dependency_feature]

            self.dependency_software.setText(dependency.software)
            self.dependency_feature.setText(dependency.feature)
        except KeyError:
            pass

    def load_software_category(self):
        """
        * Loads Software_category
        """

        try:
            category = self.soft_category_box.currentText()
            software_category = self.feature.dependencies[category]

            self.software_category.setText(software_category.category)
            self.unlock_year.setText(software_category.unlock)
        except KeyError:
            pass

    def update_software_fields(self):
        """
        * Sets the tag text for each tag in software.
        *
        * Try set software tags method
        * Show message 'Changes made'
        * Display error message if Attribute Error occurs
        """

        # try:
        set_software_tags(self)
        set_main_fields(self)
        self.statusBar().showMessage('Changes made', 1500)
        # except AttributeError:
        #     self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def update_feature(self):
        """
        * Updates attributes and etree_element_text
        * for currently selected feature
        *
        * Try to execute self.feature methods
        * set_etree_element_text and check_attribute
        * Display message if AttributeError occurs
         """

        attributes = {
            'Research': self.research_check_box.isChecked(),
            'Vital': self.vital_radio_button.isChecked(),
            'Forced': self.forced_radio_button.isChecked(),
            'From': self.from_radio_button.isChecked()
        }
        from_text = str(self.fromEdit.text())
        try:
            self.feature.set_etree_element_text()
            self.feature.check_attribute(attributes, from_text)
        except AttributeError:
            self.statusBar().showMessage('Error, Have you opened or created a mod?', 1500)

    def rename_feature(self):
        """
        * Renames currently selected feature
        *
        * Rename self.feature
        """

        name = str(self.newNameEdit.text())
        if name:
            self.feature.rename(name)

    def add_feature(self):
        """
        * Adds feature to tree
        *
        * Create Feature Object
        """

        name = str(self.featureNameEdit.text())
        features = self.tree.find('Features')
        if name:
            Feature.add(features, name, self.feature_box)

    def delete_feature(self):
        """
        * Deletes current feature
        *
        * Delete currently selected feature
        """

        feature_name = str(self.feature_box.currentText())
        if feature_name:
            self.feature.delete(self.feature.combobox)

    def add_dependency(self):
        """
        * Create dependency object for self.feature
        * Add software dependency
        * Display messages in case of NameError or AttributeError
        """

        try:
            dependency_feature = str(self.dependency_feature.text())
            software = str(self.dependency_software.text())
            if dependency_feature and software:
                self.feature.add_special_tag('d', software, dependency_feature, self.dependency_box)
                self.load_feature()
        except NameError:
            self.statusBar().showMessage('Error adding dependency', 1750)
        except AttributeError:
            self.statusBar().showMessage('Load Feature')

    def add_software_category(self):
        """
        * Create software category object for self.feature
        * Add software category
        * Display messages in case of NameError or AttributeError
        """

        try:
            category = str(self.software_category.text())
            unlock = str(self.unlock_year.text())
            if category and unlock:
                self.feature.add_special_tag('sc', category, unlock, self.soft_category_box)
                self.load_feature()
        except NameError:
            self.statusBar().showMessage('Error adding software category', 1750)
        except AttributeError:
            self.statusBar().showMessage('Load Feature')

    def delete_dependency(self):
        """
        * Deletes dependency
        * Clear dependency_software and dependency_feature line edits
        """

        dependency_feature = self.dependency_box.currentText()
        if dependency_feature:
            self.feature.delete_special_tag('d', dependency_feature, self.dependencyComboBox)
            index = self.dependency_box.currentIndex()
            self.dependency_box.removeItem(index)
            self.dependency_software.clear()
            self.dependency_feature.clear()

    def delete_software_category(self):
        """
        * Deletes software category
        * Clear software_category and unlock_year line edits
        """

        software_category = self.soft_category_box.currentText()
        if software_category:
            self.feature.delete_special_tag('sc', software_category, self.soft_category_box)
            index = self.soft_category_box.currentIndex()
            self.soft_category_box.removeItem(index)
            self.software_category.clear()
            self.unlock_year.clear()


def main():
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
