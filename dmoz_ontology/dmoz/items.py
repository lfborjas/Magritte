# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class DmozItem(Item):
	parent_category = Field() #the parent of this category
	title = Field() #the title of this category
	path = Field()
	url = Field()
	resources = Field(default = []) # the sites in this category: {title, desc, link}
	#sub_categories = Field(default = []) #a dict of categories under this one: {title, desc}


class DmozResource(Item):
	category = Field() #the ontology path to here
	name = Field() #the name of this resource
	url = Field() #the url to this resource
	description = Field()
	retrieved_on = Field() #when was it retrieved
	lang = Field(default = 'en') #the language of this resource
	type = Field(default = 'html')
	content = Field(default = '')
