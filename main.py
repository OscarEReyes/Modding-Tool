import sys
from os import path
from lxml import etree
from PyQt4 import QtGui
import design
import modEditor as mEditor
import errorMessages as em
from six import string_types
		
class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
		self.setupUi(self)
		self.openButton.clicked.connect(self.open_file_handler)
		self.saveButton.clicked.connect(lambda:self.save(self.tree))
		self.savechanges.clicked.connect(self.apply_changes_to_feature)
		self.newModButton.clicked.connect(self.create_new_mod)
		self.confirmButton.clicked.connect(self.edit_Tree)
		self.editFeatureBttn.clicked.connect(self.populate_feature_fields)
		self.changeFeatNameBttn.clicked.connect(self.change_feature_name)
		self.editCategoryButton.clicked.connect(self.load_category)
		self.saveCategoryChanges.clicked.connect(self.save_category_changes)
		self.addFeatureBttn.clicked.connect(self.add_feature)
		self.addCategoryButton.clicked.connect(self.add_category)
		self.deleteFeatureBttn.clicked.connect(lambda:self.delete_object(self.featureComboBox,self.features, 'f'))
		self.removeCategoryButton.clicked.connect(lambda:self.delete_object(self.CATEGORYCOMBOBOX, self.categories,'f'))
		self.deleteDependencyBttn.clicked.connect(lambda:self.delete_object(self.dependencyComboBox,self.dependencies,'d'))
		self.addCustomDependencyButton.clicked.connect(self.add_custom_dependency)
		self.addOSDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Operating System', self.os_dict, str(self.OSDEPBOX.currentText())))
		self.addVisualDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Visual', self.visual_dict, str(self.VISUALDEPBOX.currentText)))
		self.addAudioDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Audio', self.audio_dict, str(self.AUDIODEPBOX.currentText())))

		self.FORCEDCHECKBOX.stateChanged.connect(self.check_forced_checkbox_status)
		self.FROMCHECKBOX.stateChanged.connect(self.check_from_checkbox_status)
		self.VITALCHECKBOX.stateChanged.connect(self.check_vital_checkbox_status)
		self.OSCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.OSCHECKBOX,self.addOSDependencyBttn))
		self.VISCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.VISCHECKBOX,self.addVisualDependencyBttn))
		self.AUDCHECKBOX.stateChanged.connect(lambda:self.dependency_check_status(self.AUDCHECKBOX,self.addAudioDependencyBttn))
		self.CATEGORIESCHECKBOX.stateChanged.connect(self.categories_check_status)
		self.categories_status = False
		self.feature_index = 0
		self.os_dict = {}
		self.audio_dict = {}
		self.visual_dict = {}
		self.c_dependency_dict = {}

		self.softwareEdit = [
			self.nameGeneratorEdit, self.descriptionEdit, self.categoryEdit,
			self.ossEdit, self.randomEdit, self.nameEdit, self.fUnlockEdit,
			self.retentionEdit, self.populationEdit, self.iterativeEdit,
			self.houseEdit 
		]

		self.f_dict = {
				"Server":self.serverEdit, "Unlock":self.unlockEdit,
				"DevTime":self.devtimeEdit, "CodeArt":self.codeartEdit,
				"Description":self.descEdit, "Usability":self.usabilityEdit,
				"Stability":self.stabilityEdit, "Innovation":self.innovationEdit,
				}

		self.tagDict = {
			'Unlock':self.cUnlockEdit,
			'TimeScale':self.cTimeScaleEdit,
			'Popularity':self.cPopularityEdit,
			'Retention':self.cRetentionEdit,
			'Iterative':self.cIterativeEdit,
			'Description':self.cDescriptionEdit,
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
		message = """You are about to exit. All unsaved progress will be lost.
					 Do you wish to continue?"""
		choice = QtGui.QMessageBox.question(self, "Warning",message,
				 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:																
			sys.exit()			

	def execute_save(self):
		self.save(self.tree)																			

	def open_file_handler(self):
		self.file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		self.directory = path.dirname(self.file_name)
		self.open_file()

	def open_file(self):	
		""" Opens the xml file the user chooses and parses it. It then
			enables buttons and fields and allows the user to 
			customize his file'"""

		things_to_enable = [
				self.dependencyComboBox, self.deleteDependencyBttn,
				self.featureComboBox, self.editFeatureBttn, 
				self.changeFeatNameBttn,self.addFeatureBttn, 
				self.funcName, self.confirmButton,
				self.CATEGORIESCHECKBOX
				]		
		try:
			with open(self.file_name) as f:	
				parser = etree.XMLParser(remove_blank_text = True)
				self.tree = etree.parse(f, parser)	
			self.enable_multiple_objects(things_to_enable,True)
			self.populate_software_type_fields()
			self.features = self.tree.find('Features')	
			combobox = self.featureComboBox												
			self.add_to_combobox(combobox, self.features,'d')  
		
			if self.tree.find("Categories") is not None:  
				combobox = self.CATEGORYCOMBOBOX                                                  													
				self.add_to_combobox(combobox, self.categories, 'd')

			self.statusBar().showMessage('File Opened',1500)	

		except:
			if self.file_name == '':
				pass
			else:
				em.showUnexpectedError(self)

	def save(self, tree):
		""" Saves the file to current directory."""

		try:
			with open(self.file_name, 'wb+') as f:														
				tree.write(f, pretty_print=True)														
			self.statusBar().showMessage('Saved',1500)	

		except:
			if self.file_name == '':																		
				em.showSaveError(self)																	
			else: 
				em.showUnexpectedError(self)

	def save_as(self,tree):
		""" This function is tied to save As option and so it will ask
		 	for a file name and a new directory in case the user wishes
		 	to change where the file is saved"""

		try:
			self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save As')
			self.directory = QtGui.QFileDialog.getExistingDirectory(self, 'Choose your directory')	
			filename = path.basename(path.normpath(self.file_name))

			with open(self.file_name,'wb') as file:
				tree.write(file, pretty_print=True)

			with open(self.directory,'w') as directory:
				directory.write(file_name)
			self.statusBar().showMessage('Saved',1500)
			
		except:
			self.statusBar().showMessage('Failed to Save',1500)

	def create_new_mod(self):
		""" Runs code from a modBuilder module and creates an xml file
			with the necessary fields to make a mod. """

		try:
			self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose a name for your mod')
			number_Of_Features = self.numberOfFeatures.value()														
			mEditor.create_mod(number_Of_Features,self.file_name)	

			self.open_file()
			self.statusBar().showMessage('New Mod Created',1500)		

		except:
			pass

	def populate_software_type_fields(self):
		""" Populates the text fields in the GUI this program uses. It
			looks for the expected tags in the mod, gets their text, 
			and displays it on the correct field so the user can see 
			what it is and change it if desired. """

		try:
			tags_list = [
				'Name', 'Description', 'Unlock', 'Population' ,
				'Random' ,'Category', 'InHouse', 'OSSpecific' ,
				'Iterative','Retention','NameGenerator'
				]

			text_list = [str(tree.find(tag).text) for tag in tags_list]

			if self.tree.find("Categories") is not None:
				self.CATEGORIESCHECKBOX.setCheckState(True)

			for index, line in enumerate(self.softwareEdit):
				line.setText(text_list[index])

		except:
			self.statusBar().showMessage('An error occured',1500)											

	def load_category(self):
		try:
			name = self.CATEGORYCOMBOBOX.currentText()
			index = self.get_index(self.categories, name, 'f')

			self.category = self.categories[index]
			mEditor.set_field_text(self.tagDict, self.category)
		except:
			self.statusBar().showMessage('An error occured.',1500)	

	def add_category(self):
		""" Adds a Category to the tag Categories. It then creates the
			tags needed and adds the correct text to each."""

		field_dict = {
				'Name':self.categoryNameEdit,
				'Description':self.cDescriptionEdit,
				'Unlock':self.cUnlockEdit,
				'Popularity':self.cPopularityEdit,
				'TimeScale':self.cTimeScaleEdit,
				'Retention':self.cRetentionEdit,
				'Iterative':self.cIterativeEdit,
				'NameGenerator':self.cNameGeneratorEdit
			}

		Categories = self.tree.find('Categories')
		mEditor.add_category(self, Categories, field_dict)

	def save_category_changes(self):
		""" This function will save any changes made to the category
			that was edited"""

		try:	
			mEditor.set_tag_text(self.tagDict, self.category, 'nc')

		except:
			self.statusBar().showMessage('An error occured.',1500)

	def add_to_combobox(self,combobox,parent,item):
		""" Clears the combobox to avoid duplicates and goes
			and adds the appropiate objects. """

		try:
			combobox.clear()
			if item == 'c' and parent is not None:
				for child in parent:
					combobox.addItem(child.text)
			else:
				for child in parent:
					combobox.addItem(child.find('Name').text)
		except:
			self.statusBar().showMessage('An error occured',1500)

	def delete_object(self,combobox,parent,t):
		""" Deletes object from combobox and parent"""

		try:	
			name = str(self.combobox.currentText())					                                                          
			index = self.get_index(parent, name, t)   
			parent.remove(parent[index])      

			self.combobox.removeItem(self.combobox.currentIndex())   

		except:		
			if combobox.count() == 0:													
				self.statusBar().showMessage('There is nothing to delete',1500)	            
			else:  
				self.statusBar().showMessage('An error occured.',1500) 	

	def get_index(self,parent,name, t):
		""" This function gets the index of the wanted object"""

		idx = 0

		if t == 'f':
			if any(child.find('Name').text == name for idx, child in enumerate(parent)):
				return idx
		else:
			if any(child.text == name for idx, child in enumerate(parent)):																
				return idx 

	def populate_feature_fields(self):
		""" Displays the information of a feature selected by the user.
		"""
		self.dependencies = feature.find("Dependencies")	
		feature_name = self.featureComboBox.currentText()

		try:
			self.feature_index = self.get_index(self.features, feature_name, 'f') 
			feature = self.features[self.feature_index]	
			mEditor.set_tag_text(self.f_dict, feature, 'nc')
			
			combobox = self.dependencyComboBox			   
			self.add_to_combobox(combobox, self.dependencies, 'c')	

			self.addCustomDependencyButton.setEnabled(True)
			self.deleteFeatureBttn.setEnabled(True)
		except:
			self.statusBar().showMessage('An error occured',1500)

	def edit_Tree(self): 
		""" Removes the Categories tag if self.categories_status is
			False. If it exists, it will look for the expected tags,
			and assign the required text. The sets the tag text for 
			each tag in software"""

		tag_dict = [
			'Random','OSSpecific', 'InHouse', 'Category',
			'Name', 'Description', 'Unlock','Population',
			'Iterative','Retention', 'NameGenerator'
			] 

		Categories = self.tree.find("Categories")
			
		try:
			if self.categories_status is False and Categories is not None:
				Categories.getparent().remove(Categories)

			text_dict = dict(zip(tag_dict, self.softwareEdit))
			mEditor.set_tag_text(text_dict, self.tree, 'nc')

			self.statusBar().showMessage('Changes made',1500)
		except:
			self.statusBar().showMessage('An error occured',1500)	                							 	

	def add_feature(self):
		""" Add a feature by copying an existing feature and adds it to
			the Features tag in the tree."""

		name = self.funcName.text()
		function_exists = self.check_if_feature_exists(name)	
		combobox = self.featureComboBox												
		if name and not function_exists:
			mEditor.add_feature(self.features, name)																									
			self.add_to_combobox(combobox, self.features, 'd')	
			self.statusBar().showMessage('Feature Created',1500)
		else:																			
			em.show_name_taken(self)															 

	def change_feature_name(self):
		""" This function is used to change the name of a feature in both the
			xml file and in the feature combobox."""

		f_name = str(self.featureComboBox.currentText())
		text = str(self.newNameEdit.text())

		# Changes the text value for the Name tag in the selected feature
		index = self.get_index(self.features, f_name, 'f')
		self.features[index].find("Name").text = text 

		# Sets new text for the selected feature to reflect the name change
		index = self.featureComboBox.currentIndex()
		self.featureComboBox.setItemText(index, self.newNameEdit.text())

		#Clears the newNameEdit field
		self.newNameEdit.clear()

	def check_if_feature_exists(self,name):			
		""" Checks if there is a feature in features with a certain
			name and return a boolean value. """	

		if any(feature.find('Name').text == name for feature in self.features):
			return True
		return False  		

	def apply_changes_to_feature(self):	
		""" Updates the selected feature's information. The feature is
			updated to reflect the changes that were made on the GUI. 
			Dictionaries are then cleared to prevent adding things more
			than once """

		feature = self.features[self.feature_index]	
		depbox_list = [
				self.OSDEPBOX, self.VISUALDEPBOX, self.AUDIODEPBOX
				]
		try:
			# Sets the appropiate text values for each tag in feature.
			mEditor.set_tag_text(self.f_dict, feature, 'nc')

			# Enables and/or clear fields and manages dependencies.				
			self.enable_multiple_objects(depbox_list, True)
			self.clear_fields()
			self.dependency_managing()	

			# Checks for attributes and takes action if necessary.												
			self.check_for_attributes(feature)														
			if self.From_Status:
				feature.attrib['From'] = str(self.fromLE.text())

			self.statusBar().showMessage('Saved changes to feature',1500)							
		except:
			em.errorWhileSaving(self)											

	def dependency_managing(self):
		""" Manages dependencies. Creates a dependencies tag if it does
			not exist yet and stores it in self.dependencies for easy
			access. Then adds the necessary dependencies to the current
			feature, add custom dependencies and adds dependencies to 
			the dependencies combobox. """
			
		dependency_dict_list = [
			self.os_dict, self.visual_dict, self.audio_dict
			]	
		feature = self.features[self.feature_index]
		dependencies = self.dependencies

		try:
			mEditor.add_Dependencies(dependencies, dependency_dict_list)		

			combobox = self.dependencyComboBox
			mEditor.add_custom_dependencies(dependencies, self.c_dependency_dict)
			self.add_to_combobox(combobox, self.dependencies, 'c')

		except:
			pass

	def add_custom_dependency(self):
		""" Adds a custom depencency if it does not already exist """

		software = str(self.softwareDepLE.text())
		feature = str(self.featureDepLE.text())

		if software and feature:
			self.check_for_feature(feature, software, self.c_dependency_dict)	
		else:
			em.showNoSoftwareNoFeatureError(self)                                     	

	def check_for_feature(self, feature, software, dependency_dict):
		""" Checks if the feature the dependency depends on is part of
			the custom dependency dictionary which is used when adding
			custom dependencies. """

		dependency_dict.setdefault(software, feature)

		if feature not in dependency_dict[software]:
			dependency_dict[software].append(feature)	
		else:
			self.statusBar().showMessage('Cannot add same dependency twice.',1500)					

	def check_for_attributes(self,feature):
		""" Checks for attributes. Runs the first three functions to
			check the status of the vital,from, and forced
			checkboxes. """

		self.check_vital_checkbox_status()
		self.check_from_checkbox_status()
		self.check_forced_checkbox_status()

		attribute_dict = {
			'Vital':self.Vital_Status,
			'Forced':self.Forced_Status,
			'From':self.From_Status
			}

		for attribute, status in attribute_dict.items():
			if status:
				feature.attrib[attribute] = 'TRUE'

			elif attribute in feature.attrib and not status:
				del feature.attrib[attribute]

	def enable_multiple_objects(self, things_to_enable, state):
		""" Iterates over a lists and enables or disables the fields in
			that list. """

		for thing in things_to_enable:
			thing.setEnabled(state)	
	
	def add_needed_dependency(self,d_type, d_dict, dependency):  
		d_dict.setdefault(dependency, d_type)

	def categories_check_status(self):
		""" Checks if the categories checkbox is selected and performs
			the required actions. """

		field_list = [
				self.cDescriptionEdit, self.removeCategoryButton, 
				self.editCategoryButton, self.cPopularityEdit, 
				self.cTimeScaleEdit, self.addCategoryButton, 
				self.cUnlockEdit, self.saveCategoryChanges,
				]

		Categories = self.tree.find("Categories")
		self.categories_status = self.CATEGORIESCHECKBOX.isChecked()

		if self.categories_status and Categories is None:
			self.enable_multiple_objects(field_list, True)
			self.categories = etree.SubElement(self.tree.getparent(), 'Categories')
		else:
			self.CATEGORYCOMBOBOX.clear()          
			self.enable_multiple_objects(field_list, False)

	def dependency_check_status(self, checkbox, button):       
		""" Enables button if checkbox is checked when triggered. """ 
			  
		status =  checkbox.isChecked()
		button.setEnabled(status)

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

	def clear_fields(self):
		dict_set= [
			self.c_dependency_dict, self.os_dict, 
			self.visual_dict, self.audio_dict
			]

		for item in dict_set:
			item.clear()   
		for key, value in self.f_dict.items():
			value.clear() 

def main():
	app = QtGui.QApplication(sys.argv)
	global form
	form = MainWindow()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
