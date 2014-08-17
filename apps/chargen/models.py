from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Character(models.Model):
	"""
	Character model class.
	"""
    name = models.CharField(max_length=255)
    stats = models.ManyToManyField('CharacterStat')
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    portrait = models.ImageField(
		upload_to="portraits", null=True, blank=True)
    user = models.ForeignKey(User)
    race = models.ForeignKey('Race')
    posessions = models.ManyToManyField(
		'Posession',null=True, blank=True)
    weapons = models.ManyToManyField('Weapon',null=True, blank=True)
    cls = models.ForeignKey('Cls') #change to ManyToMany later 
                                   #to allow multiclass
    
    step = models.IntegerField(default=1) #where the character is 
                                          #in the creation process.
                                          #Not yet handled by app.
    details = models.OneToOneField('Details',null=True, blank=True)
    
    number_of_spells = models.IntegerField(
		default=1,null=True, blank=True)
    spells = models.ManyToManyField('Spell',null=True, blank=True) 
    hp = models.IntegerField(default=0,null=True, blank=True)
    skills = models.ManyToManyField('CharSkill', null=True)
    armor = models.ManyToManyField('Armor', null=True)
    
    def __unicode__(self):
        return self.name

class Proficiency(models.Model):
	"""
	Not currently in use.
	
	Represents a sort of sub-skill at which characters may be 
	proficient. Generally used for weapons proficencies, e.g. 
	if a character has the "Sword" proficiency he or she has been
	trainined with that particular weapon and can use it without 
	penalty.
	"""
	
    name = models.CharField(max_length=60)
    
    def __unicode__(self):
        return self.name

class Details(models.Model):
	"""
	Miscellaneous personal properties of the character.
	""" 
    alignment = models.CharField(max_length=40)
    height = models.CharField(max_length=40)
    weight = models.CharField(max_length=40)
    hair = models.CharField(max_length=40)
    eyes = models.CharField(max_length=40)
    story = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return "Details..."
        
class CharacterStat(models.Model):
	"""
	Properties of one particular Stat on one Character.
	e.g. a Character's STR of 17.
	"""
    name = models.ForeignKey('Stat') #STR, CON, DEX, etc.
    value = models.IntegerField()
    value_suffix = models.IntegerField(null=True, blank=True) 
    #e.g. for STR 18/00
    
    def __unicode__(self):
        return self.name.abbreviation

class Stat(models.Model):
	"""
	A statistic type available to characters. Usually these would be 
	a fixed list of STR, DEX, CHA, CON, INT, WIS but making this a
	class instead of a list allows admins to add house-rule stats to 
	the list, e.g. COM (Comeliness) or LUK (Luck).  
	"""
    name = models.CharField(max_length=35)
    abbreviation = models.CharField(max_length=6)
    ability_modifiers = models.ManyToManyField(
		'AbilityModifier', null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
class Race(models.Model):
	"""
	A race such as Elf, Dwarf, etc. Race affects a character's stats, 
	and choices for races should be limited by Stat values.
	""" 
    name = models.CharField(max_length=60)
    stat_adjustments = models.ManyToManyField(
		'StatModifier', null=True, blank=True)
    stat_minimums = models.ManyToManyField(
		'StatMinimum', null=True, blank=True)
    stat_maximums = models.ManyToManyField(
		'StatMaximum', null=True, blank=True)
    abilities = models.ManyToManyField(
		'RacialAbility', null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class Spell(models.Model):
	"""
	Represents a magic spell that can be known by a character.
	"""
    name = models.CharField(max_length=60)
    
    def __unicode__(self):
        return self.name
        
class Skill(models.Model):
	"""
	A skill that can be chosen by a character.
	"""
    name = models.CharField(max_length=60)
    initial_value = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
        
class CharSkill(models.Model):
	"""
	A particular skill (with score) for a particular character.
	"""
    name = models.CharField(max_length=60)
    value = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name        
        
class StatModifier(models.Model):
	"""
	Represents an adjustment to be made to a Stat for a certain Race,
	e.g. Elves get +1 to DEX and -1 to CON.
	"""
    name = models.ForeignKey('Stat')
    value = models.IntegerField()
    
class StatMinimum(models.Model):
	"""
	Required minimum for a Stat for a particular Race. E.g. a user 
	can't choose Elf for his Race unless he has a DEX of 10 or more.
	"""
    name = models.ForeignKey('Stat')
    value = models.IntegerField()
    
class StatMaximum(models.Model):
	"""
	Required maximum for a Stat for a particular Race. E.g. a user 
	can't choose Elf if his STR is 18 or higher.
	"""
    name = models.ForeignKey('Stat')
    value = models.IntegerField()
        
class Posession(models.Model):
	"""
	A generic item available to be owned by a Character, e.g. 50' rope.
	"""
    name = models.CharField(max_length=60)
    weight = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
        
class Armor(models.Model):
	"""
	A type of armor available to be worn by a Character. E.g. Chainmail.
	"""
	#TODO: Implement allowed_classes property to limit armor choices to
	#certain classes, e.g. Mages can't choose Plate Armor.
    name = models.CharField(max_length=60)
    weight = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    ac_modifier = models.IntegerField()
    
    def __unicode__(self):
        return self.name

class Weapon(models.Model):
	"""
	A type of weapon available to be owwned by a Character, 
	e.g. Longsword.
	"""
    name = models.CharField(max_length=60)
    weight = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    allowed_classes = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

class Cls(models.Model):  
	"""
	A Class is a Character's chosen profession type, e.g. Mage.
	"""
    name = models.CharField(max_length=60)
    abilities = models.ManyToManyField(
		'ClassAbility', null=True, blank=True)
    allowed_races = models.ManyToManyField('Race')
    minimum_stat_values = models.ManyToManyField(
		'StatMaximum', null=True, blank=True)
    maximum_stat_values = models.ManyToManyField(
		'StatMinimum', null=True, blank=True)
    allowed_weapons = models.ManyToManyField(
		'Weapon', null=True, blank=True)
    number_of_proficiencies = models.IntegerField(default=1)
    #level_thresholds = models.ManyToManyField(LevelThreshold)
    
    def __unicode__(self):
        return self.name
    
class RacialAbility(models.Model):
	"""
	A special talent granted by Race, e.g. Dwarves have a special talent 
	for underground navigation.
	"""
    name = models.CharField(max_length=60)
    explanation = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class ClassAbility(models.Model):
	"""
	A special talent granted by class. E.g. Paladins can heal once 
	per day.
	"""
    name = models.CharField(max_length=60)
    explanation = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
class AbilityModifier(models.Model):
	"""
	A bouns or penalty applied to an ability, skill, activity, etc., 
	as determined by the value of a Stat. E.g. high INT grants a bonus 
	to the maximum number of spells a character can concurrently 
	memorize.
	"""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=12)
    stat_value = models.IntegerField()
    mod_value = models.CharField(max_length=100, null=True, blank=True)
    
    def __unicode__(self):
        return self.abbreviation + " " + str(self.stat_value)
    
