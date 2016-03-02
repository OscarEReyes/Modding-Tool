import sys
from os import path
from six import string_types
from lxml import etree
from PyQt4 import QtGui
import design
import modEditor as mEditor
import errorMessages as em	

class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
		self.setupUi(self)
		self.openButton.clicked.connect(self.open_file_handler)
		self.saveButton.clicked.connect(lambda:self.save(self.tree))
		self.newModButton.clicked.connect(self.create_new_mod)
		self.saveSoftwareButton.clicked.connect(self.apply_changes_to_tree)

		# Feature Buttons #
		self.editFeatureButton.clicked.connect(self.fill_feature_fields)
		self.savechanges.clicked.connect(self.apply_changes_to_feature)
		self.changeFeatureNameButton.clicked.connect(self.change_feature_name)
		self.addFeatureButton.clicked.connect(self.add_feature)
		self.deleteFeatureButton.clicked.connect(lambda:self.delete_object(self.featureComboBox,self.features, 'f'))

		# Category Buttons #
		self.editCategoryButton.clicked.connect(self.load_category)
		self.saveCategoryChanges.clicked.connect(self.save_category_changes)
		self.addCategoryButton.clicked.connect(self.add_category)
		self.removeCategoryButton.clicked.connect(lambda:self.delete_object(self.CATEGBOX, self.categories,'f'))

		# Depenendency buttons #
		self.deleteDependencyBttn.clicked.connect(lambda:self.delete_object(self.dependencyComboBox,self.dependencies,'d'))
		self.addCustomDependencyButton.clicked.connect(self.add_custom_dependency)
		self.addOSDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Operating System', self.os_dict, self.OSDEPBOX))
		self.addVisualDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Visual', self.visual_dict, self.VISUALDEPBOX))
		self.addAudioDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Audio', self.audio_dict, self.AUDIODEPBOX))

		# State Change functions. # 
		self.FORCEDCHECKBOX.stateChanged.connect(self.check_forced_checkbox_status)
		self.FROMCHECKBOX.stateChanged.connect(self.check_from_checkbox_status)
		self.VITALCHECKBOX.stateChanged.connect(self.check_vital_checkbox_status)
		self.OSCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.OSCHECKBOX,self.addOSDependencyBttn))
		self.VISCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.VISCHECKBOX,self.addVisualDependencyBttn))
		self.AUDCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.AUDCHECKBOX,self.addAudioDependencyBttn))
		self.CATEGCHECKBOX.stateChanged.connect(self.categories_check_status)

		self.categories_status = False
		self.os_dict = {}
		self.audio_dict = {}
		self.visual_dict = {}
		self.c_dependency_dict = {}

		self.softwareDict = {
			'Name':self.nameEdit,
			'Category':self.categoryEdit,
			'Description':self.descriptionEdit,
			'Random':self.randomEdit,
			'Unlock':self.unlockEdit,
			'Population':self.populationEdit,
			'OSSpecific':self.ossEdit,
			'InHouse':self.houseEdit,
			'Retention':self.retentionEdit,
			'Iterative':self.iterativeEdit,
			'NameGenerator':self.nameGeneratorEdit
		}
		self.featureDict = {
				"Description":self.fDescEdit,
				"Unlock":self.fUnlockEdit,
				"DevTime":self.devtimeEdit,
				"Innovation":self.innovationEdit,
				"Usability":self.usabilityEdit,
				"Stability":self.stabilityEdit,
				"CodeArt":self.codeartEdit,
				"Server":self.serverEdit, 
				}
		self.categoryDict = {
			'Name':self.categoryNameEdit,
			'Description':self.cDescriptionEdit,
			'Unlock':self.cUnlockEdit,
			'Popularity':self.cPopularityEdit,
			'TimeScale':self.cTimeScaleEdit,
			'Retention':self.cRetentionEdit,
			'Iterative':self.cIterativeEdit,
			'NameGenerator':self.cNameGeneratorEdit
			}
		mainMenu = self.menuBar()
		fileMenu = self.add_menu_to_menubar(mainMenu, '&File')
		self.define_action(mainMenu,fileMenu,"&Close", "Ctrl+Q", self.close)
		self.define_action(mainMenu,fileMenu,"&Save As", "", self.save_as)
		self.define_action(mainMenu,fileMenu,"&Save", "Ctrl+S" ,self.execute_save)
		self.define_action(mainMenu,fileMenu,"&New Mod", "Ctrl+N" ,self.create_new_mod)	

	def add_menu_to_menubar(self, menu,name):
		return menu.addMenu(name)		

	def add_actions_to_menubar(self, file_menu,action):
		file_menu.addAction(action)		

	def define_action(self, menu_bar, file_menu, action_name, shortcut, function):
		action = QtGui.QAction(action_name, self)
		if shortcut:
			action.setShortcut(shortcut)
		action.triggered.connect(function)
		self.add_actions_to_menubar(file_menu,action)

	def close(self):
		message = ("You are about to exit. All unsaved progress will be lost."
				   " Do you wish to continue?")
		choice = QtGui.QMessageBox.question(self, "Warning",message,
				 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:																
			sys.exit()			

	def execute_save(self):
		self.save(self.tree)																			

	def open_file_handler(self):
		self.file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		self.directory = path.dirname(self.file_name)
		self.open_file(self.file_name)

	def open_file(self, file_name):	
		""" Opens and parses an xml file. Enables buttons & fields"""

		things_to_enable = [
				self.dependencyComboBox, self.deleteDependencyBttn,
				self.featureComboBox, self.editFeatureButton, 
				self.changeFeatureNameButton,self.addFeatureButton, 
				self.featureNameEdit, self.saveSoftwareButton,
				self.CATEGCHECKBOX
				]		
		try:
			with open(file_name) as f:	
				parser = etree.XMLParser(remove_blank_text = True)
				self.tree = etree.parse(f, parser)	

			self.populate_software_type_fields()
			self.features = self.tree.find('Features')	
			self.add_to_combobox(self.featureComboBox, self.features, 'd')  
		
			if self.tree.find("Categories") is not None:  
				self.add_to_combobox(self.CATEGBOX , self.categories, 'd')
				
			self.enable_multiple_objects(things_to_enable,True)
			self.statusBar().showMessage('File Opened',1500)	
		except FileNotFoundError:
				pass

	def save(self, tree):
		""" Saves the file to current directory."""

		with open(self.file_name, 'wb+') as f:														
			tree.write(f, pretty_print = True)														
		self.statusBar().showMessage('Saved',1500)	

	def save_as(self):
		""" Save As Function. Self-explanatory"""

		try:
			self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save As')
			self.directory = QtGui.QFileDialog.getExistingDirectory(self, 'Choose your directory')	
			filename = path.basename(path.normpath(self.file_name))

			with open(self.file_name,'wb') as file:
				self.tree.write(file, pretty_print=True)
			with open(self.directory,'w') as directory:
				directory.write(file_name)
				
			self.statusBar().showMessage('Saved',1500)
		except FileNotFoundError:
			self.statusBar().showMessage('Failed to Save',1500)

	def create_new_mod(self):
		""" Creates an xml file with the required fields. """

		number_of_features = self.featureNum.value()
		self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose a name for your mod')													
		mEditor.create_mod(number_of_features, self.file_name)	

		self.open_file(self.file_name)
		self.statusBar().showMessage('New Mod Created',1500)	

	def add_to_combobox(self, combobox, parent, item):
		""" Adds object to a combobox """

		if parent is not None:
			combobox.clear()
			if item == 'c':
				for child in parent:
					combobox.addItem(child.text)
			else:
				for child in parent:
					combobox.addItem(child.find('Name').text)

	def delete_object(self, combobox, parent,t):
		""" Deletes object from combobox and parent"""

		try:	
			name = str(combobox.currentText())	
			index = self.get_index(parent, name, t)  
			parent.remove(parent[index])      
			combobox.removeItem(combobox.currentIndex())   

		except IndexError:														
			self.statusBar().showMessage('There is nothing to delete',1500)	            

	def get_index(self,parent,name, t):
		""" This function gets the index of the wanted object"""

		idx = 0
		if t == 'f':
			if any(child.find('Name').text == name for idx, child in enumerate(parent)):
				return idx
		else:
			if any(child.text == name for idx, child in enumerate(parent)):																
				return idx 	

	def apply_changes_to_tree(self): 
		""" Sets the tag text for each tag in software. Removes the 
			Categories tag if self.categories_status is False otherwise
			it assigns the appropiate text to each tag """

		Categories = self.tree.find("Categories")
		if not self.categories_status and Categories is not None:
			Categories.getparent().remove(Categories)
		mEditor.set_tag_text(self.softwareDict, self.tree, 'nc')
		self.statusBar().showMessage('Changes made',1500)    

	def populate_software_type_fields(self):
		""" Populates the appropiate text fields in the GUI. """

		if self.tree.find("Categories") is not None:
			self.CATEGCHECKBOX.setCheckState(True)

		tags_list = [key for key in self.softwareDict]
		field_list = [value for key, value in self.softwareDict.items()]
		text_list = [str(self.tree.find(tag).text) for tag in tags_list]
		
		for index, field in enumerate(field_list):
			field.setText(text_list[index])									

	def load_category(self):
		name = self.CATEGBOX.currentText()
		index = self.get_index(self.categories, name, 'f')
		if name and index is not None:
			try: 
				self.category = self.categories[index]
				mEditor.set_field_text(self.categoryDict, self.category)
			except IndexError:
				self.statusBar().showMessage('Index Error',1500)

	def add_category(self):
		""" Adds a Category to the tag Categories. Then creates the
			tags needed and assigns the correct text to each."""

		field_dict = self.categoryDict.copy()
		field_dict.pop('Name', None)	

		Categories = self.tree.find('Categories')
		mEditor.add_category(self, Categories, field_dict)

	def save_category_changes(self):
		""" Saves changes made to the edited category"""

		if self.category is not None:	
			mEditor.set_tag_text(self.categoryDict, self.category, 'nc')

	def fill_feature_fields(self):
		""" Displays the information of a feature selected by the user.
		"""

		feature_name = self.featureComboBox.currentText()
		index = self.get_index(self.features, feature_name, 'f') 
		self.feature = self.features[index]	
		self.dependencies = self.feature.find("Dependencies")	
	
		if self.feature is not None:
			mEditor.set_field_text(self.feature, self.featureDict)
			self.add_to_combobox(self.dependencyComboBox, self.dependencies, 'c')	

			self.addCustomDependencyButton.setEnabled(True)
			self.deleteFeatureButton.setEnabled(True)            							 	

	def add_feature(self):
		""" Add a feature by copying an existing feature and adds it to
			the Features tag in the tree."""

		name = str(self.featureNameEdit.text())
		function_exists = any(feature.find('Name').text == name for feature in self.features)
	
		if name and not function_exists:
			mEditor.add_feature(self.features, name)								
			self.add_to_combobox(self.featureComboBox, self.features, 'd')	
			self.statusBar().showMessage('Feature Created', 1500)
		else:																			
			em.show_name_taken(self)		

	def change_feature_name(self):
		""" This function is used to change the name of a feature in both the
			xml file and in the feature combobox."""

		feature_name = str(self.featureComboBox.currentText())
		text = str(self.newNameEdit.text())

		# Changes the text value for the Name tag in the selected feature
		index = self.get_index(self.features, feature_name, 'f')
		self.features[index].find("Name").text = text 

		# Sets new text for the selected feature to reflect the name change
		index = self.featureComboBox.currentIndex()
		self.featureComboBox.setItemText(index, self.newNameEdit.text())

		#Clears the newNameEdit field
		self.newNameEdit.clear()

	def apply_changes_to_feature(self):	
		""" Updates the selected feature's information. Then updates feature 
		"""
		try:
			depbox_list = [
					self.OSDEPBOX, 
					self.VISUALDEPBOX, 
					self.AUDIODEPBOX
					]
			# Sets the appropiate text values for each tag in feature.
			mEditor.set_tag_text(self.featureDict, self.feature, 'nc')
			# Enables and/or clear fields and manages dependencies.				
			self.enable_multiple_objects(depbox_list, True)
			self.add_dependencies()	
			self.clear_fields()
			# Checks for attributes and takes action if necessary.												
			self.check_for_attributes(self.feature)														
			self.statusBar().showMessage('Saved changes to feature', 1500)	
		except AttributeError:
			self.statusBar().showMessage('Select a feature to edit', 1500)

	def check_for_attributes(self,feature):
		""" Checks for attributes. Runs the first three functions to
			check the status of the vital,from, and forced
			checkboxes. """

		attribute_dict = {
			'Vital': self.Vital_Status,
			'Forced': self.Forced_Status,
			}
		for attribute, status in attribute_dict.items():
			if status:
				feature.attrib[attribute] = 'TRUE'

			elif attribute in feature.attrib and not status:
				del feature.attrib[attribute]	

		if self.From_Status:
				self.feature.attrib['From'] = str(self.fromEdit.text())	
		elif 'From' in feature.attrib and not self.From_Status: 
			del feature.attrib['From']

	def check_forced_checkbox_status(self):
		""" Checks if forced checkbox and then enables 
			or disables the other two checkboxes """

		self.Forced_Status = self.FORCEDCHECKBOX.isChecked() 													
		self.FROMCHECKBOX.setEnabled(not self.Forced_Status)    	   												
		self.VITALCHECKBOX.setEnabled(not self.Forced_Status) 	   											

	def check_vital_checkbox_status(self):
		""" Checks if vitalcheckbox is checked and then enables or
			disables FORCEDCHECKBOX """

		self.Vital_Status = self.VITALCHECKBOX.isChecked() 													
		self.FORCEDCHECKBOX.setEnabled(not self.Vital_Status)	

	def check_from_checkbox_status(self):		
		""" Checks the status of the from checkbox and then enables or
			disables FORCEDCHECKBOX """	

		self.From_Status = self.FROMCHECKBOX.isChecked() 														
		self.FORCEDCHECKBOX.setEnabled(not self.From_Status)									 

	def categories_check_status(self):
		""" Checks if the categories checkbox is selected and performs
			the required actions. """

		button_list = [
				self.saveCategoryChanges, self.removeCategoryButton, 
				self.editCategoryButton, self.addCategoryButton,
				]
		Categories = self.tree.find("Categories")
		self.categories_status = self.CATEGCHECKBOX.isChecked()
		if self.categories_status and Categories is None:
			self.enable_multiple_objects(button_list, True)
			self.categories = etree.SubElement(self.tree.getparent(), 'Categories')
		else:
			self.CATEGBOX.clear()          
			self.enable_multiple_objects(field_list, False)

	def dependency_check_status(self, checkbox, button):       
		""" Enables button if checkbox is checked when triggered. """ 
			  
		status =  checkbox.isChecked()
		button.setEnabled(status)				

	def add_dependencies(self):
		""" Creates a dependencies tag if it does not exist yet. Then 
			adds the necessary dependencies to the current feature, add
			custom dependencies and adds dependencies to the
			dependencies combobox. """
			
		dependency_dicts = [
			self.os_dict, self.visual_dict, self.audio_dict
			]	
		mEditor.add_dependencies_to_feature(self.dependencies, dependency_dicts)		
		mEditor.add_custom_dependencies(self.dependencies, self.c_dependency_dict)
		self.add_to_combobox(self.dependencyComboBox, self.dependencies, 'c')

	def add_needed_dependency(self, software, d_dict, combobox): 
		dependency = str(combobox.currentText()) 
		d_dict.setdefault(dependency, software)

	def add_custom_dependency(self):
		""" Adds a custom depencency if it does not already exist """

		software = str(self.softwarEdit.text())
		feature = str(self.featureEdit.text())
		if software and feature:
			dependency_dict.setdefault(software, feature)
			if feature not in self.c_dependency_dict[software]:
				self.c_dependency_dict[software].append(feature)	
			else:
				self.statusBar().showMessage('Cannot add same dependency twice.',1500)	
		else:
			em.showNoSoftwareNoFeatureError(self)                                     	

	def enable_multiple_objects(self, things_to_enable, state):
		""" Iterates over a lists and enables or disables the fields in
			that list. """

		for thing in things_to_enable:
			thing.setEnabled(state)	

	def clear_fields(self):
		self.c_dependency_dict.clear()
		self.os_dict.clear()
		self.visual_dict.clear()
		self.audio_dict.clear()
		for key, value in self.featureDict.items():
			value.clear() 

def main():
	app = QtGui.QApplication(sys.argv)
	global form
	form = MainWindow()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
