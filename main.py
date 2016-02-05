from lxml import etree
from PyQt4 import QtGui
import sys
import design
import modBuilder as mb
import errorMessages as em
from os import path
from copy import deepcopy
from six import string_types
		
class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
		self.setupUi(self)
		self.openButton.clicked.connect(lambda:self.open_file_handler())
		self.saveButton.clicked.connect(lambda:self.save(self.tree))
		self.savechanges.clicked.connect(lambda:self.apply_changes_to_feature())
		self.newModButton.clicked.connect(lambda:self.create_new_mod())
		self.confirmButton.clicked.connect(lambda: self.find_tree_tags())
		self.deleteFeatureBttn.clicked.connect(lambda:self.delete_feature(str(self.featureComboBox.currentText())))
		self.editFeatureBttn.clicked.connect(lambda:self.populate_feature_fields(self.featureComboBox.currentText()))
		self.changeFeatNameBttn.clicked.connect(lambda:self.change_feature_name())

		self.addFeatureBttn.clicked.connect(lambda:self.add_feature(self.funcName.text(),len(self.features)))
		self.addCategoryButton.clicked.connect(lambda:self.add_category(self.tree.find('Categories')))
		self.removeCategoryButton.clicked.connect(lambda:self.delete_category(self.CATEGORYCOMBOBOX.currentText()))
		self.editCategoryButton.clicked.connect(lambda:self.load_category(self.CATEGORYCOMBOBOX.currentText()))
		self.saveCategoryChanges.clicked.connect(lambda:self.save_category_changes())
		self.addOSDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Operating System', self.os_dict, str(self.OSDEPBOX.currentText())))
		self.addVisualDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Visual', self.visual_dict, str(self.VISUALDEPBOX.currentText)))
		self.addAudioDependencyBttn.clicked.connect(lambda:self.add_needed_dependency('Audio', self.audio_dict, str(self.AUDIODEPBOX.currentText())))
		self.addCustomDependencyButton.clicked.connect(lambda:self.add_custom_dependency(str(self.softwareDepLE.text()),str(self.featureDepLE.text())))
		self.deleteDependencyBttn.clicked.connect(lambda:self.delete_dependency(self.dependencyComboBox.count(),str(self.dependencyComboBox.currentText())))

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
		self.custom_Dependency_Dict = {}
		self.softwareEdit = [
			self.ossEdit, self.populationEdit, self.nameEdit, self.fUnlockEdit,
			self.nameGeneratorEdit, self.descriptionEdit, self.iterativeEdit,
			self.retentionEdit, self.randomEdit, self.categoryEdit, 
			self.houseEdit
		]
		mainMenu = self.define_menubar()
		fileMenu = self.add_menu_to_menubar(mainMenu, '&File')
		self.define_action(mainMenu,fileMenu,"&Close","Ctrl+Q",self.close)
		self.define_action(mainMenu,fileMenu,"&Save As","",self.save_as)
		self.define_action(mainMenu,fileMenu,"&Save","Ctrl+S",self.execute_save)
		self.define_action(mainMenu,fileMenu,"&New Mod","Ctrl+N",self.create_new_mod)

	def define_menubar(self):
		return self.menuBar()		

	def add_menu_to_menubar(self,menu,name):
		return menu.addMenu(name)		

	def add_actions_to_menubar(self,file_Menu,action):
		file_Menu.addAction(action)		

	def define_action(self,menu_bar,file_menu,action_name,shortcut,function):
		action = QtGui.QAction(action_name, self)
		if shortcut:
			action.setShortcut(shortcut)
		action.triggered.connect(function)
		self.add_actions_to_menubar(file_menu,action)

	def close(self):
		choice = QtGui.QMessageBox.question(self, 'Warning',"You are about to exit. All unsaved progress will be lost. Do you want to continue?"
											,QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:																
			sys.exit()			

	def execute_save(self):
		self.save(self.tree)																			

	def open_file_handler(self):
		self.file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		self.directory = path.dirname(self.file_name)
		self.open_file()

	def open_file(self):	
		""" This function is tied to a "Open File" Button and what it 
			does is open the xml file the user chooses and parses it.
			It then enables some other buttons,loads information to 
			text fields add information from the xml file to comboboxes
			and basically allows the user to see what matters and what 
			he might want to change or delete in this XML file that 
			will ultimately be used as a mod in the game 'Software Inc'"""

		try:
			with open(self.file_name) as f:	
				parser = etree.XMLParser(remove_blank_text=True)
				self.tree = etree.parse(f, parser)														 
			self.features = self.tree.find('Features')												
			list_of_things_to_enable = [
				self.addFeatureBttn, self.funcName, self.confirmButton,
				self.CATEGORIESCHECKBOX
				]
			self.enable_multiple_objects(list_of_things_to_enable,True)
			self.populate_software_type_fields()													
			self.add_features_to_combobox()  														
			self.add_categories_to_combobox()

			self.statusBar().showMessage('File Opened',1500)	
		except:
			if self.file_name == '':
				pass
			else:
				em.showUnexpectedError(self)

	def save(self, tree):
		""" This function saves the file to current directory."""
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

			with open(self.file_name,'wb') as f:
				tree.write(f, pretty_print=True)

			with open(self.directory,'w') as d:
				d.write(file_name)
			self.statusBar().showMessage('Saved',1500)
		except:
			self.statusBar().showMessage('Failed to Save',1500)

	def create_new_mod(self):
		""" This function is tied to a button "Create new mod" and what
			it does is run code from a module imported and creates an 
			xml files with the nessecary fields to make a mod. This 
			file is created with a name given by the user in a 
			directory chosen by the user and is then opened using the
			open function shown above"""
		try:
			self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose a name for your mod')
			number_Of_Features = self.numberOfFeatures.value()														
			mb.createMod(number_Of_Features,self.file_name)													
			self.open_file()
			self.statusBar().showMessage('New Mod Created',1500)											
		except:
			pass

	def populate_software_type_fields(self):
		""" This function will populate the text fields in the GUI that
		 	this program uses. It looks for the expected tags in the 
		 	mod, gets their text, and displays it on the correct field
			so the user can see what it is and change it if desired."""
		try:
			tags_to_look_for = [
				'Name', 'Description', 'Unlock','Population', 'Random','Category',
				'InHouse', 'OSSpecific', 'Iterative','Retention', 'NameGenerator'
				]

			tag_text_list = []

			for tag in tags_to_look_for:
				tag_text_list.append(str(self.tree.find(tag).text))
			if self.tree.find("Categories") is not None:
				self.CATEGORIESCHECKBOX.setCheckState(True)

			for index,line in enumerate(self.softwareEdit):
				line.setText(tag_text_list[index])
		except:
			self.statusBar().showMessage('An error occured',1500)											


	def categories_check_status(self):
		""" This function checks if the categories checkbox is selected
			and performs the required actions. If it is selected, then
			it must create a subElement called Categories so that the 
			user may add a Category element, and it will enable the 
			required fields. However, if it is not checked then it 
			disables the fields and sets the class varaible 
			self.categories_status variable to False"""
		try:
			list_of_lines = [
				self.editCategoryButton, self.cPopularityEdit, self.cTimeScaleEdit,
				self.addCategoryButton, self.cUnlockEdit, self.saveCategoryChanges,
				self.cDescriptionEdit, self.removeCategoryButton, 
				]

			self.categories_status = self.CATEGORIESCHECKBOX.isChecked()
			if self.categories_status:
				self.enable_multiple_objects(list_of_lines,True)
				root = self.tree.getroot()
				if self.tree.find("Categories") is None:
					etree.SubElement(root,'Categories')
				self.categories = self.tree.find("Categories")
			else:
				self.CATEGORYCOMBOBOX.clear()          
				self.enable_multiple_objects(list_of_lines, False)
		except:
			self.statusBar().showMessage('An error occured',1500)											


	def add_categories_to_combobox(self): 
		""" This feature clears the category combobox to avoid adding
			the same category multiple times. It then goes through each
			category in categories(if the tag Categories exists) and 
			adds the text value of Name for each category. In simple 
			terms, it looks for each category, looks for the obligatory
			Name tag, and gets the text found in the Name tag to 
			display in the combobox."""

		self.CATEGORYCOMBOBOX.clear()          
		if self.tree.find("Categories") is not None:                                                    
			for category in self.tree.find("Categories"):   
				self.CATEGORYCOMBOBOX.addItem(category.find('Name').text)

	def add_category(self,Categories):
		""" This function will add a Category to the tag Categories. It
			then creates the tags needed and adds the correct text to
			each."""
		try:
			name = str(self.categoryNameEdit.text())
			if  name:
				category_index = self.CATEGORYCOMBOBOX.count()
				etree.SubElement(Categories,'Category')

				dict_of_fields = {
				'Name':self.categoryNameEdit,
				'Description':self.cDescriptionEdit,
				'Unlock':self.cUnlockEdit,
				'Popularity':self.cPopularityEdit,
				'TimeScale':self.cTimeScaleEdit,
				'Retention':self.cRetentionEdit,
				'Iterative':self.cIterativeEdit,
				'NameGenerator':self.cNameGeneratorEdit
				}
				for tag,field in dict_of_fields.items():
					etree.SubElement(Categories[category_index],tag).text = str(field.text())
				
				self.add_categories_to_combobox()
		except:
			self.statusBar().showMessage('An error occured.',1500)


	def save_category_changes(self):
		""" This function will save any changes made to the category
			that was edited"""
		try:	
			tag_dict = {
				'Unlock':self.cUnlockEdit,
				'TimeScale':self.cTimeScaleEdit,
				'Popularity':self.cPopularityEdit,
				'Retention':self.cRetentionEdit,
				'Iterative':self.cIterativeEdit,
				'Description':self.cDescriptionEdit,
				'NameGenerator':self.cNameGeneratorEdit
				}

			for tag,field in tag_dict.items():
				self.category.find(tag).text = field.text()
		except:
			self.statusBar().showMessage('An error occured.',1500)

	def delete_category(self,category_to_delete):
		""" Deletes the selected category from the file and from the category combobox"""
		try:
			category_key = self.get_category_index(self.tree,feature_to_delete) 									
			self.categories.getparent().remove(self.categories[category_key])                                                		
	
			category_index = self.CATEGORYCOMBOBOX.findText(category_to_delete) 						    
			self.CATEGORYCOMBOBOX.removeItem(category_index) 
		except:
			self.statusBar().showMessage('An error occured.',1500)


	def get_category_index(self, name):  
		""" Is used to find the index of a category."""

		for idx, category in enumerate(self.categories):
			if category.find('Name').text == name:
				return idx			

	def load_category(self,name):
		try:
			index = self.get_category_index(name)
			self.category = self.categories[index]

			tag_dict = {
				'Unlock':self.cUnlockEdit,
				'TimeScale':self.cTimeScaleEdit,
				'Popularity':self.cPopularityEdit,
				'Retention':self.cRetentionEdit,
				'Iterative':self.cIterativeEdit,
				'Description':self.cDescriptionEdit,
				'NameGenerator':self.cNameGeneratorEdit
				}

			for tag,field in tag_dict.items():
				field.setText(self.category.find(tag).text)
		except:
			self.statusBar().showMessage('An error occured.',1500)

	def populate_feature_fields(self,feature_name):
		""" This function displayes the information of a feature
			selected by the user. The user selects a feature on a
			combobox and clicks on a button called "Edit Feature."This
			function will find the index of the feature using the name
			displayed in the combobox, it then looks for the expected 
			tags and displays the text values for each tag in the right
			text field. Finally, this function creates a class variable
			for self.dependencies. This is so other functions can use a 
			variable holding the Dependency tag in the feature selected 
			without having to use the .find etree method over and over 
			again. The dependencies of the feature are also added to a 
			combobox"""

		try:
			self.feature_index = self.get_feature_index(feature_name) 
			feature = self.features[self.feature_index]

			tag_dict = {
				self.stabilityEdit:'Stability', self.innovationEdit:'Innovation',
				self.descEdit:'Description', self.usabilityEdit:'Usability',
				self.devtimeEdit:'DevTime', self.codeartEdit:'CodeArt',
				self.serverEdit:'Server', self.unlockEdit:'Unlock'

				}
			for field,tag in tag_dict.items():
				field.setText(feature.find(tag).text)

			self.addCustomDependencyButton.setEnabled(True)
			self.deleteFeatureBttn.setEnabled(True)
			self.dependencies = feature.find("Dependencies")				   
			self.add_dependencies_to_combobox()	
		except:
			self.statusBar().showMessage('An error occured',1500)

	def find_tree_tags(self): 
		""" This function will remove the Categories tag if 
			self.categories_status is False and if it exists. 
			It then looks for the expected tags, and assigns the 
			required text."""
		try:
			if  self.categories_status is False:
				if self.tree.find("Categories") is not None:
					self.tree.find("Categories").getparent().remove(self.tree.find("Categories"))
			tags_to_look_for = [
				'Name','Description',
				'Unlock','Population',
				'Random','OSSpecific',
				'InHouse','Category',
				'Iterative','Retention',
				'NameGenerator'
				]

			tag_text_dict = dict(zip(tags_to_look_for,self.softwareEdit))

			for tag,field in tag_text_dict.items(): 
				self.tree.find(tag).text = str(field.text()) 	

			self.statusBar().showMessage('Changes made',1500)
		except:
			self.statusBar().showMessage('An error occured',1500)	                							 	

	def add_feature(self,name,count):
		""" This function will add a feature. It copies an alreadyvo
		 	existing feature and adds it to the Features tag in the
		 	tree."""

		functionExists = self.check_if_feature_exists(name)											
		if name and  not functionExists:													
			new_feature = deepcopy(self.features[0])												
			for tag in new_feature:																	
				tag.text = ''																		
			new_feature.find('Name').text = name 													
			self.features.insert(count, new_feature)												
			self.add_features_to_combobox()																	
			self.statusBar().showMessage('Feature Created',1500)									
		else:																			
			em.showNoFeatureNameError(self)															

	def delete_feature(self,feature_to_delete):
		""" This function deletes the selected feature from the
			features tag and from the feature combobox """

		featureKey = self.get_feature_index(feature_to_delete) 
		feature = self.features[featureKey]								
		self.features.remove(feature)                                                	
		feature_index = self.featureComboBox.currentIndex()						    
		self.featureComboBox.removeItem(feature_index)     

	def change_feature_name(self):
		""" This function is used to change the name of a feature in both the
			xml file and in the feature combobox."""

		featureName = str(self.featureComboBox.currentText())
		featureIndex = self.get_feature_index(featureName)
		self.features[featureIndex].find("Name").text = str(self.newNameEdit.text())

		comboboxIndex = self.featureComboBox.currentIndex()
		self.featureComboBox.setItemText(comboboxIndex,self.newNameEdit.text())
		self.newNameEdit.clear()

	def check_if_feature_exists(self,name):			
		""" This function will check if there is a feature in features
			with a certain name and return True if it exists or False
			if it does not."""		

		if any(feature.find('Name').text == name for feature in self.features):
			return True
		return False  		

	def get_feature_index(self, name):  															
		"""This function gets the index of a certain feature"""
		for idx, feature in enumerate(self.features):
			if feature.find('Name').text == name:
				return idx

	def apply_changes_to_feature(self):	
		""" This function will update the information for the feature
			that was edited. The feature is updated to reflect the 
			changes that were made on the GUI. This then ends in the
			clearing of some dictionaries to prevent adding things more
			than one the next time and displays a message to let the 
			user knowthat the changes were saved."""

		try:
			feature = self.features[self.feature_index]											
				
			feature_information_dict = {
				"Server":self.serverEdit, "Unlock":self.unlockEdit,
				"DevTime":self.devtimeEdit, "CodeArt":self.codeartEdit,
				"Description":self.descEdit, "Usability":self.usabilityEdit,
				"Stability":self.stabilityEdit, "Innovation":self.innovationEdit,
				}
					
			for tag,field in feature_information_dict.items():									
				feature.find(tag).text = str(field.text())		

			depBoxList = [self.OSDEPBOX, self.VISUALDEPBOX, self.AUDIODEPBOX]							
			self.enable_multiple_objects(depBoxList,True)
			self.dependency_managing()													
			self.check_for_attributes(feature)														
			self.clear_fields()

			if self.From_Status:
				feature.attrib['From'] = str(self.fromLE.text())
			self.statusBar().showMessage('Saved changes to feature',1500)							
		except:
			em.errorWhileSaving(self)
	
	def add_features_to_combobox(self): 
		""" This function clears the feature combobox to avoid 
			duplicates and goes through each feature in features and
			adds the text value for the name tag in each feature."""
		try:
			list_of_things_to_enable = [
				self.dependencyComboBox, self.deleteDependencyBttn,
				self.featureComboBox, self.editFeatureBttn, 
				self.changeFeatNameBttn
				]		
			self.featureComboBox.clear()

			for feature in self.features:	
				self.featureComboBox.addItem(feature.find('Name').text)													
			self.enable_multiple_objects(list_of_things_to_enable,True)	
		except:
			self.statusBar().showMessage('An error occured',1500)													

	def dependency_managing(self):
		""" This function manages dependencies. It creates a 
			dependencies tag if it does not exist yet and then stores 
			it in self.dependencies for easy access. After that it will
			add the necessary dependencies to the selected feature, add
			custom dependencies, and adds dependencies to the 
			dependencies combobox. """
		try:
			if self.dependencies is None:																	
				etree.SubElement(self.features[self.feature_index],"Dependencies")					
				self.dependencies = (self.features[self.feature_index].find("Dependencies"))				
			self.add_Dependencies()														
			self.add_custom_dependencies()
			self.add_dependencies_to_combobox()
		except:
			pass

	def get_dependency_index(self,name):													
		""" This function gets the index of the dependency selected"""
		for idx, dependency in enumerate(self.dependencies):															
			if dependency.text == name:																
				return idx 

	def add_dependencies_to_combobox(self):
		""" This function clears the dependency combobox and then adds
			the text value for the name tag in each dependency in
			dependencies"""

		self.dependencyComboBox.clear()		
		try:										
			for index,dependency in enumerate(self.dependencies):
				self.dependencyComboBox.addItem(self.dependencies[index].text )
		except:
			pass									

	def add_Dependencies(self):
		""" This function adds the dependencies in a feature using 
			dictionaries. Everytime a feature is loaded, its 
			dependencies are added to dictionaries. There are three
			for each type of software that the dependencies can be 
			categorized as."""

		dependency_dict_list = [self.os_dict,self.visual_dict,self.audio_dict]	

		for dependency_dict in dependency_dict_list:	                                               
			for feature,Software in dependency_dict.items():											
				dependency_in_feature = self.check_if_dependency_is_in_feature(feature)                  
				if not dependency_in_feature:																  
					etree.SubElement(self.dependencies,"Dependency",Software = Software).text = feature	   
		self.add_dependencies_to_combobox()                                                              

	def check_if_dependency_is_in_feature(self,feature):
		""" Checks if the dependency is in the current feature."""
		for dependency in self.dependencies:
			if dependency.text == feature:
				return True
		return False

	def add_custom_dependency(self,software,feature):
		""" adds a custom depdencency. Note: it executes the 
			check_for_feature function to check if it already exists
			and takes the desired action"""

		if software and feature: 														
			self.check_for_feature(feature,software,self.custom_Dependency_Dict)	
		else:
			em.showNoSoftwareNoFeatureError(self)                                          	

	def check_for_feature(self,feature,software,custom_dependency_dict):
		""" This function checks if the feature the dependency depends
			on is part of the custom dependency dictionary which is 
			used when adding custom dependencies"""
			
		custom_dependency_dict.setdefault(software,feature)
		if feature not in custom_dependency_dict[software]:
			list_of_features = custom_dependency_dict[software]
			is_string = isinstance(list_of_features,string_types)	
			if is_string == True:
				list_of_features = list(list_of_features)
			list_of_features.append(feature)
			custom_dependency_dict[software] = list_of_features	
		else:
			self.statusBar().showMessage('Cannot add same dependency twice.',1500)					

	def add_custom_dependencies(self):
		""" This goes through the custom_Dependency_Dict and adds
			dependencies to the current feature"""

		for software,features in self.custom_Dependency_Dict.items():
			is_string = isinstance(features,string_types)	
			if is_string:
				etree.SubElement(self.dependencies,"Dependency", Software = software).text = features 
			else:
				for  feature in features:
					etree.SubElement(self.dependencies,"Dependency", Software = software).text = feature 
																		
	def check_for_attributes(self,feature):
		""" This function checks for attributes. Runc the first three 
			functions to check the status of the vital,from, and forced
			checkboxes since they user might have not clicked on those 
		    checkboxes and thus failed tu have runned these functions 
		    that create the required class variables self.Vital_Status,
		    self.Forced_Status, and self.From_Status. Dependending on 
		    those statuses it will give an attribute to the feature or
		    not."""

		self.check_vital_checkbox_status()
		self.check_from_checkbox_status()
		self.check_forced_checkbox_status()
		attribute_Dict = {
			'Vital':self.Vital_Status,
			'Forced':self.Forced_Status,
			'From':self.From_Status
			}
		for attribute,status in attribute_Dict.items():
			if status:
				feature.attrib[attribute] = 'TRUE'
			elif attribute in feature.attrib and not status:
				del feature.attrib[attribute]


	def enable_multiple_objects(self,list_of_things_to_enable,state):
		""" This function just iterates over a lists and enables or
			disables the fields in that list. Made it a function
			since it is used a few times."""

		for object_to_enable in list_of_things_to_enable:
			object_to_enable.setEnabled(state)	
	
	def add_needed_dependency(self,dependency_type,dependency_dict,dependency_selected):  
		dependency_dict.setdefault(dependency_selected,dependency_type)

	def delete_dependency(self,number_Of_Dependencies,dependency_name):
		""" This function deletes a dependency from dependencies and 
			from the dependency combobox."""
		try:						                                                          
			index = self.get_dependency_index(dependency_name)    
			self.dependencies.remove(self.dependencies[index])       
			combobox_index = self.dependencyComboBox.currentIndex()
			self.dependencyComboBox.removeItem(combobox_index)    												
		except:		
			if self.dependencyComboBox.count() == 0:													
				self.statusBar().showMessage('There are no dependencies to delete',1500)	            
			else:  
				em.showUnexpectedError(self) 					

	def dependency_check_status(self,checkbox,button):       
		""" This function enables a button is a checkbox is checked. 
			Triggered by the statechange of some checkboxes."""   

		status =  checkbox.isChecked()
		button.setEnabled(status)

	def check_forced_checkbox_status(self):
		""" Checks the status of the forced checkbox and then enables 
			or disables the other two checkboxes dependending on the 
			the value of forced status"""

		self.Forced_Status = self.FORCEDCHECKBOX.isChecked() 													
		self.FROMCHECKBOX.setEnabled(not self.Forced_Status)    	   												
		self.VITALCHECKBOX.setEnabled(not self.Forced_Status) 	   											

	def check_vital_checkbox_status(self):
		""" Checks the status of the vital checkbox and then enables or
			disables the FORCEDCHECKBOX dependending on the the value 
			of vital status"""

		self.Vital_Status = self.VITALCHECKBOX.isChecked() 													
		self.FORCEDCHECKBOX.setEnabled(not self.Vital_Status)	

	def check_from_checkbox_status(self):		
		""" Checks the status of the from checkbox and then enables or
			disables the FORCEDCHECKBOX dependending on the the value 
			of from status"""	

		self.From_Status = self.FROMCHECKBOX.isChecked() 														
		self.FORCEDCHECKBOX.setEnabled(not self.From_Status)																													

	def clear_fields(self):
		clearSet = [
			self.custom_Dependency_Dict, self.codeartEdit, self.innovationEdit,
			self.os_dict, self.serverEdit, self.unlockEdit, self.stabilityEdit,  
			self.devtimeEdit, self.visual_dict, self.audio_dict, self.descEdit, 
			self.usabilityEdit
			]
		for item in clearSet:
			item.clear()    

def main():
	app = QtGui.QApplication(sys.argv)
	global form
	form = MainWindow()
	form.show()
	app.exec_()
if __name__ == '__main__':
	main()
