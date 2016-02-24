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
		self.openButton.clicked.connect(self.open_file_handler)
		self.saveButton.clicked.connect(lambda:self.save(self.tree))
		self.savechanges.clicked.connect(self.apply_changes_to_feature)
		self.newModButton.clicked.connect(self.create_new_mod)
		self.confirmButton.clicked.connect(self.find_tree_tags)
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
		self.custom_Dependency_Dict = {}

		self.softwareEdit = [
			self.ossEdit, self.populationEdit, self.nameEdit, self.fUnlockEdit,
			self.nameGeneratorEdit, self.descriptionEdit, self.iterativeEdit,
			self.retentionEdit, self.randomEdit, self.categoryEdit, 
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
		self.define_action(mainMenu,fileMenu,"&Close","Ctrl+Q",self.close)
		self.define_action(mainMenu,fileMenu,"&Save As","",self.save_as)
		self.define_action(mainMenu,fileMenu,"&Save","Ctrl+S",self.execute_save)
		self.define_action(mainMenu,fileMenu,"&New Mod","Ctrl+N",self.create_new_mod)	

	def add_menu_to_menubar(self,menu,name):
		return menu.addMenu(name)		

	def add_actions_to_menubar(self,file_menu,action):
		file_menu.addAction(action)		

	def define_action(self,menu_bar,file_menu,action_name,shortcut,function):
		action = QtGui.QAction(action_name, self)
		if shortcut:
			action.setShortcut(shortcut)
		action.triggered.connect(function)
		self.add_actions_to_menubar(file_menu,action)

	def close(self):
		message = """You are about to exit. All unsaved progress will be lost. Do you wish to continue?"""
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

		#try:
		with open(self.file_name) as f:	
			parser = etree.XMLParser(remove_blank_text=True)
			self.tree = etree.parse(f, parser)														 
		self.features = self.tree.find('Features')	

		self.enable_upon_opening()
		self.populate_software_type_fields()

		combobox = self.featureComboBox												
		self.add_to_combobox(combobox, self.features,'d')  
		if self.tree.find("Categories") is not None:  
			combobox = self.CATEGORYCOMBOBOX                                                  													
			self.add_to_combobox(combobox, self.categories, 'd')

		self.statusBar().showMessage('File Opened',1500)	
		#except:
		#if self.file_name == '':
		#	pass
		#else:
		#	em.showUnexpectedError(self)

	def enable_upon_opening(self):
		things_to_enable = [
				self.dependencyComboBox, self.deleteDependencyBttn,
				self.featureComboBox, self.editFeatureBttn, 
				self.changeFeatNameBttn,self.addFeatureBttn, 
				self.funcName, self.confirmButton,
				self.CATEGORIESCHECKBOX
				]		
		self.enable_multiple_objects(things_to_enable,True)

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

			with open(self.file_name,'wb') as f:
				tree.write(f, pretty_print=True)

			with open(self.directory,'w') as d:
				d.write(file_name)
			self.statusBar().showMessage('Saved',1500)
		except:
			self.statusBar().showMessage('Failed to Save',1500)

	def create_new_mod(self):
		""" Runs code from a modBuilder module and creates an xml file
			with the necessary fields to make a mod. """
		try:
			self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose a name for your mod')
			number_Of_Features = self.numberOfFeatures.value()														
			mb.createMod(number_Of_Features,self.file_name)													
			self.open_file()
			self.statusBar().showMessage('New Mod Created',1500)											
		except:
			pass

	def populate_software_type_fields(self):
		""" Populates the text fields in the GUI this program uses. It
			looks for the expected tags in the mod, gets their text, 
			and displays it on the correct field so the user can see 
			what it is and change it if desired. """

		#try:
		text_list = []
		tags_list = [
			'Name', 'Description', 'Unlock', 'Population' ,
			'Random' ,'Category', 'InHouse', 'OSSpecific' ,
			'Iterative','Retention','NameGenerator'
			]

		for tag in tags_list:
			text = str(self.tree.find(tag).text)
			text_list.append(text)

		if self.tree.find("Categories") is not None:
			self.CATEGORIESCHECKBOX.setCheckState(True)

		for index,line in enumerate(self.softwareEdit):
			text = text_list[index]
			line.setText(text)
		#except:
			#self.statusBar().showMessage('An error occured',1500)											

	def categories_check_status(self):
		""" Checks if the categories checkbox is selected and performs
			the required actions. """
		try:
			field_list = [
				self.editCategoryButton, self.cPopularityEdit, self.cTimeScaleEdit,
				self.addCategoryButton, self.cUnlockEdit, self.saveCategoryChanges,
				self.cDescriptionEdit, self.removeCategoryButton, 
				]

			self.categories_status = self.CATEGORIESCHECKBOX.isChecked()
			if self.categories_status:
				self.enable_multiple_objects(field_list,True)
				root = self.tree.getroot()
				if self.tree.find("Categories") is None:
					self.categories = etree.SubElement(root,'Categories')
			else:
				self.CATEGORYCOMBOBOX.clear()          
				self.enable_multiple_objects(field_list, False)
		except:
			self.statusBar().showMessage('An error occured',1500)											

	def add_category(self):
		""" Adds a Category to the tag Categories. It then creates the
			tags needed and adds the correct text to each."""
		try:
			Categories = self.tree.find('Categories')
			name = str(self.categoryNameEdit.text())
			if  name:
				category_index = self.CATEGORYCOMBOBOX.count()
				etree.SubElement(Categories,'Category')
				category = Categories[category_index]

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
				self.set_tag_text(dict_of_fields, category , 'c')
				if self.tree.find("Categories") is not None:        
					combobox = self.CATEGORYCOMBOBOX                                            
					self.add_to_combobox(combobox, self.categories, 'd')
		except:
			self.statusBar().showMessage('An error occured.',1500)

	def save_category_changes(self):
		""" This function will save any changes made to the category
			that was edited"""
		try:	
			self.set_tag_text(self.tagDict, self.category, 'nc')
		except:
			self.statusBar().showMessage('An error occured.',1500)

	def load_category(self):
		#try:
		name = self.CATEGORYCOMBOBOX.currentText()
		index = self.get_index(self.categories, name, 'f')

		self.category = self.categories[index]
		self.set_field_text(self.tagDict, self.category )
		#except:
			#self.statusBar().showMessage('An error occured.',1500)

	def add_to_combobox(self,combobox,parent,item):
		""" Clears the combobox to avoid duplicates and goes
			and adds the appropiate objects. """
		#try:
		combobox.clear()
		if item == 'c':
			if parent is not None:
				for child in parent:
					combobox.addItem(child.text)
		else:
			for child in parent:
				combobox.addItem(child.find('Name').text)
		#except:
			#self.statusBar().showMessage('An error occured',1500)

	def delete_object(self,combobox,parent,t):
		""" Deletes object from combobox and parent"""
		try:	
			name = str(self.combobox.currentText())					                                                          
			index = self.get_index(parent, name, t)   
			dependency = parent[index]
			parent.remove(dependency)      

			index = self.combobox.currentIndex()
			self.combobox.removeItem(index)    												
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

	def set_tag_text(self, dictionary, parent, t):
		for key, value in dictionary.items():	
			text = str(value.text())
			if t == "c":
				etree.SubElement(parent,key).text = text
			else: 
				parent.find(key).text = text	

	def set_field_text(self,parent):
		for line_edit, tag in dictionary.items():
			text = parent.find(tag).text
			line_edit.setText(text)
			
	def populate_feature_fields(self):
		""" Displays the information of a feature selected by the user.
		"""
		#try:
		f_name = self.featureComboBox.currentText()
		self.feature_index = self.get_index(self.features, f_name, 'f') 
		feature = self.features[self.feature_index]	
		self.set_tag_text(self.f_dict, feature, 'nc')

		self.addCustomDependencyButton.setEnabled(True)
		self.deleteFeatureBttn.setEnabled(True)

		self.dependencies = feature.find("Dependencies")	
		combobox = self.dependencyComboBox			   
		self.add_to_combobox(combobox,self.dependencies,'c')	
		#except:
			#self.statusBar().showMessage('An error occured',1500)

	def find_tree_tags(self): 
		""" Removes the Categories tag if self.categories_status is
			False. If it exists, it will look for the expected tags,
			and assign the required text."""
		try:
			tag_dict = [
				'Random','OSSpecific', 'InHouse','Category',
				'Name','Description','Unlock','Population',
				'Iterative','Retention', 'NameGenerator'
				] 

			if self.categories_status is False:
				Categories = self.tree.find("Categories") 
				if Categories is not None:
					Categories.getparent().remove(Categories)

			text_dict = dict(zip(tag_dict,self.softwareEdit))
			self.set_tag_text(text_dict, self.tree, 'nc')
			self.statusBar().showMessage('Changes made',1500)

		except:
			self.statusBar().showMessage('An error occured',1500)	                							 	

	def add_feature(self):
		""" Add a feature by copying an existing feature and adds it to
			the Features tag in the tree."""
		name = self.funcName.text()
		count = len(self.features)
		function_exists = self.check_if_feature_exists(name)											
		if name and  not function_exists:													
			new_feature = deepcopy(self.features[0])												
			for tag in new_feature:																	
				tag.text = ''																		
			new_feature.find('Name').text = name 													
			self.features.insert(count, new_feature)		
			combobox = self.featureComboBox										
			self.add_to_combobox(combobox, self.features, 'd')																	
			self.statusBar().showMessage('Feature Created',1500)									
		else:																			
			em.showNoFeatureNameError(self)															 

	def change_feature_name(self):
		""" This function is used to change the name of a feature in both the
			xml file and in the feature combobox."""

		f_name = str(self.featureComboBox.currentText())
		text = str(self.newNameEdit.text())
		feature_index = self.get_index(self.features, f_name, 'f')
		feature = self.features[feature_index]
		feature.find("Name").text = text 

		index = self.featureComboBox.currentIndex()
		text = self.newNameEdit.text()
		self.featureComboBox.setItemText(index, text)
		self.newNameEdit.clear()

	def check_if_feature_exists(self,name):			
		""" This function will check if there is a feature in features
			with a certain name and return True if it exists or False
			if it does not."""		

		if any(feature.find('Name').text == name for feature in self.features):
			return True
		return False  		

	def apply_changes_to_feature(self):	
		""" Updates the selected feature's information. The feature is
			updated to reflect the changes that were made on the GUI. 
			Dictionaries are then cleared to prevent adding things more
			than once """
		try:
			depbox_list = [
				self.OSDEPBOX, self.VISUALDEPBOX, self.AUDIODEPBOX
				]

			feature = self.features[self.feature_index]											
			self.set_tag_text(self.f_dict, feature, 'nc')
										
			self.enable_multiple_objects(depbox_list, True)
			self.dependency_managing()													
			self.check_for_attributes(feature)														
			self.clear_fields()

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
		try:
			feature = self.features[self.feature_index]
			if self.dependencies is None:																	
				self.dependencies= etree.SubElement(feature,"Dependencies")					
			self.add_Dependencies()														
			self.add_custom_dependencies()
			combobox = self.dependencyComboBox
			self.add_to_combobox(combobox,self.dependencies,'c')
		except:
			pass

	def add_Dependencies(self):
		""" Adds the dependencies in a feature using dictionaries. When
			a feature is loaded, its dependencies are added to 
			dictionaries. Three for each type of software that the 
			dependencies are categorized as."""
		dependency_dict_list = [
			self.os_dict, self.visual_dict, self.audio_dict
			]	

		for dependency_dict in dependency_dict_list:	                                               
			for feature, software in dependency_dict.items():											
				dependency_exists = self.check_for_dependency(feature)                  
				if not dependency_exists:																  
					etree.SubElement(self.dependencies,"Dependency",Software = software).text = feature	   
		combobox = self.dependencyComboBox
		self.add_dependencies_to_combobox(combobox,self.dependencies,c)                                                              

	def check_for_dependency(self,feature):
		""" Checks if the dependency is in the current feature."""
		if any(dependency.text == feature for dependency in self.dependencies):
			return True
		return False

	def add_custom_dependency(self):
		""" Adds a custom depencency. Note: it executes the 
			check_for_feature function to check if it already exists
			and takes the desired action"""
		software = str(self.softwareDepLE.text())
		feature = str(self.featureDepLE.text())

		if software and feature: 														
			self.check_for_feature(feature,software,self.custom_Dependency_Dict)	
		else:
			em.showNoSoftwareNoFeatureError(self)                                          	

	def check_for_feature(self,feature,software,c_dependency_dict):
		""" Checks if the feature the dependency depends on is part of
			the custom dependency dictionary which is used when adding
			custom dependencies"""
			
		c_dependency_dict.setdefault(software,feature)
		if feature not in c_dependency_dict[software]:
			feature_list = c_dependency_dict[software]
			is_string = isinstance(feature_list,string_types)	
			if is_string:
				feature_list = list(feature_list)
			feature_list.append(feature)
			c_dependency_dict[software] = feature_list	
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
				for feature in features:
					etree.SubElement(self.dependencies,"Dependency", Software = software).text = feature 
																		
	def check_for_attributes(self,feature):
		""" Checks for attributes. Runs the first three functions to
			check the status of the vital,from, and forced
			checkboxes. """

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
		""" Iterates over a lists and enables or disables the fields in
			that list. """

		for object_to_enable in list_of_things_to_enable:
			object_to_enable.setEnabled(state)	
	
	def add_needed_dependency(self,dependency_type,dependency_dict,dependency_selected):  
		dependency_dict.setdefault(dependency_selected,dependency_type)

	def dependency_check_status(self,checkbox,button):       
		""" Enables a button if a checkbox is checked. 
			Triggered by the statechange of some checkboxes."""   
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
		clearSet = [
			self.custom_Dependency_Dict, self.codeartEdit,self.innovationEdit,
			self.os_dict, self.serverEdit, self.unlockEdit,self.stabilityEdit,  
			self.devtimeEdit,self.visual_dict, self.audio_dict, self.descEdit, 
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
