from lxml import etree

def createMod(numberOfFeatures,nameOfMod):
	numberOfFeatures = numberOfFeatures
	root = etree.Element("SoftwareType")
	createTags(root)
	addFeatures(root,numberOfFeatures)
	saveMod(root,nameOfMod)
def createTags(root):
	listOfFields = ['Name','Category', 'Description', 'Random', 'Unlock', 'OSSpecific','Population',  'InHouse','Retention','Iterative','NameGenerator']
	for name in listOfFields:
		etree.SubElement(root, name).text = ''
def addFeatures(root,numberOfFeatures):
	features = etree.SubElement(root, "Features")                   # Stores features in a variable. Did this so I could use it in the etree.SubElement(parent, child) function
	while (numberOfFeatures > 0):                                   # Uses numberOfFeatures as a counter.
		feature = etree.SubElement(features, "Feature")             # We make a feature!
		etree.SubElement(feature, "Name").text = 'Feature %s' %str(numberOfFeatures)
		populateFeature(feature)
		numberOfFeatures = numberOfFeatures - 1                     # Substracts from counter		
def populateFeature(feature):
	featureFields = ['Description','Unlock','DevTime','Innovation','Usability','Stability','CodeArt','Server']
	for field in featureFields:
		etree.SubElement(feature, field).text = ''
def saveMod(root,Name):
	saveFile = open(Name,'wb') #Typical save file. Open, and write in bytes. 
	fileToSave = (etree.tostring(root,pretty_print=True))
	saveFile.write(fileToSave) #Writes text to file
	saveFile.close() #Closes File
