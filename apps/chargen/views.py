from django.conf import settings
from chargen import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from random import randint
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
import logging

logging.basicConfig(
	filename="debuglog.txt", 
	filemode="w", 
	level=logging.INFO
	)

def dice(count, sides):
	"""Roll the dice. Get an int."""
    total = 0
    for die in range(count):
        total = total + randint(1, sides)
    return total
	
def best_x_of_y(number_of_rolls, keepers, sides):
	"""
	Simulate a number (number_of_rolls) of X-sided die rolls 
	and return the sum of the highest Y rolls. 
	(X = sides, Y = keepers)
	"""
	rolls = []
	for die in range(number_of_rolls):
		rolls.append(dice(1, sides))
	rolls = sorted(rolls)
	total = sum(rolls[-keepers:])
	return total
     
#Get the basic stats, e.g. STR, DEX, CON, etc.
basic_stats = models.Stat.objects.all()

#Below this comment are functions for specific pages. 

@login_required 
def create(request):
	"""
	Create or receive the form for the first page of the character 
	creation process. 
	"""
    class CharForm(forms.Form):
        name = forms.CharField(max_length=255)
        race = forms.ModelChoiceField(
			queryset=models.Race.objects.all())
        cls = forms.ModelChoiceField(
			queryset=models.Cls.objects.all())
        
    form_message = ""
    if request.method == 'POST': # If the form has been submitted...
        form = CharForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            character = models.Character(
                name = form.cleaned_data['name'],
                race = form.cleaned_data['race'],
                cls = form.cleaned_data['cls'],
                user = request.user
                )
            character.save()
            form_message = ""
            return HttpResponseRedirect(
				'/cg/stats/' + str(character.id)) # Redirect after POST
        else:
            form_message = "Invalid submission"
    else:
        form = CharForm() 
        # An unbound form, if the page was loaded with GET
    context = {
		'form':form, 
		"form_message":form_message
		}
    return render_to_response(
		'chargen/form.html', 
		RequestContext(request, context)
		)

@login_required       
def list(request):
	"""
	Deliver the Character objects owned by the logged-in user to the 
	list page. 
	"""
    characters = request.user.character_set.all()
    
    return render_to_response(
        "chargen/list.html", 
        RequestContext(request),
        )
        
@login_required        
def view(request, char_id):
	"""
	Deliver a specific character object to the single character 
	viewer page.
	"""
    character = models.Character.objects.get(id=char_id)
    
    context = {"character":character}
    return render_to_response(
        "chargen/charview.html", 
        RequestContext(request, context)
        )
        
@login_required        
def printview(request, char_id):
	"""
	Deliver the character object to the printer-friendly view, along 
	with a range of numbers representing a set of table columns to be 
	filled with stat-based ability modifiers.
	"""
    character = models.Character.objects.get(id=char_id)
    mod_range = range(5) #TODO: make mod_range dynamic
    
    context = {
		"character":character, 
		"mod_range":mod_range
		}
    return render_to_response(
        "chargen/charviewprint.html", 
        RequestContext(request, context)
        )
       
@login_required        
def statform(request, char_id):
	"""
	Create or handle receipt of a form that allows the user to select
	dice rolling method. For /stats page.
	"""
    character = models.Character.objects.get(id=char_id)
    class DiceForm(forms.Form):
        number_of_dice = forms.IntegerField(
            label="Roll how many dice?",
            initial=3,
            max_value=30
            )
        number_of_keepers = forms.IntegerField(
            label="and keep the best",
            initial=3,
            max_value=30
            )
        roll_adder = forms.IntegerField(
            label="Modifier to each roll",
            initial=0
            )
        number_of_rolls = forms.IntegerField(
            label="Number of rolls",
            initial=7,
            min_value=7,
            max_value=30
            )
        assignment = forms.ChoiceField(
            choices=[("1", "Allow me to assign rolls to stats"),
                ("0", "Assign rolls to stats randomly"),],  
            label="How to place rolls",
            initial="1",
            )
    form_message = ""
    if request.method == 'POST': # If the form has been submitted...
        form = DiceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            dice = form.cleaned_data['number_of_dice']
            keepers = form.cleaned_data['number_of_keepers']
            modifier = form.cleaned_data['roll_adder']
            num_rolls = form.cleaned_data['number_of_rolls']
            if keepers > dice:
                keepers = dice
            roll_values = []
            stat_count = models.Stat.objects.count()
            if num_rolls < stat_count:
                num_rolls = stat_count
            for i in range(num_rolls):
                roll = best_x_of_y(dice, keepers , 6) + modifier
                roll_values.append(roll)
            if form.cleaned_data['assignment'] == '0':
                i = 0
                for stat in models.Stat.objects.all():
                    character.stats.create(
						name=stat, value=roll_values[i])
                    character.save()
                    i += 1
                return HttpResponseRedirect(
					'/cg/basics/'+str(character.id)) 
					#Redirect after POST
            else:
                stats = models.Stat.objects.all()
                fillers = [
					"(discard)" for x in range(
						len(roll_values) - stat_count)]
                context = {
					"character":character, 
					"vals":roll_values, 
					"stats":stats, 
					'fillers':fillers
					}
                return render_to_response(
					'chargen/statsort.html', 
					RequestContext(request, context)
					)
        else:
            form = DiceForm() # An unbound form
            form_message = """There was a problem with your choices. \
				Please try again."""
    else:
        form = DiceForm() # An unbound form
        
    context = {
		'form':form, 
		"form_message":form_message, 
		"char_id":char_id
		}
    return render_to_response(
		'chargen/stats.html', 
		RequestContext(request, context)
		)
    
def basicsform(request, char_id):
	"""
	Create or handle submission of a form that allows the user to 
	enter details such as hair color, eye color, history, etc.
	"""
    character = models.Character.objects.get(id=char_id)
    class BasicsForm(forms.Form):
        height = forms.CharField(
            label="Height",
            )
        weight = forms.CharField(
            label="Weight",
            )
        hair = forms.CharField(
            label="Hair",
            )
        eyes = forms.CharField(
            label="Eyes",
            )
        alignment = forms.ChoiceField(
            choices=[
                    ("Lawful Good", "Lawful Good"),
                    ("Lawful Neutral", "Lawful Neutral"),
                    ("Lawful Evil", "Lawful Evil"),
                    ("Neutral Good", "Neutral Good"),
                    ("Neutral", "Neutral"),
                    ("Neutral Evil", "Neutral Evil"),
                    ("Chaotic Good", "Chaotic Good"),
                    ("Chaotic Neutral", "Chaotic Neutral"),
                    ("Chaotic Evil", "Chaotic Evil"),
                    ],  
            label="Alignment",
            initial="Neutral",
            )
        story = forms.CharField(
            label="History",
            widget=forms.Textarea(attrs={'rows':'14', 'columns':'80'}),
            )
    form_message = str(character.id)
    if request.method == 'POST': # If the form has been submitted...
        form = BasicsForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            hair = form.cleaned_data['hair']
            eyes = form.cleaned_data['eyes']
            alignment = form.cleaned_data['alignment']
            story = form.cleaned_data['story']
            
            #Create a new Details instance to attach to the Character
            new_details = models.Details(
                height=height,
                weight=weight,
                hair=hair,
                eyes=eyes,
                alignment=alignment,
                story=story,
                )
            new_details.save()
            
            #Apply the Details to the Character.
            character.details = new_details
            character.save()
            return HttpResponseRedirect(
				'/cg/classpage/' + str(char_id)
				)
        else:
            form = BasicsForm() # An unbound form
            form_message = """Data was not valid. \
				Make sure to enter a value for every field."""
    else:
        form = BasicsForm() # An unbound form
        
    context = {
		'form':form, 
		"form_message":form_message, 
		"char_id":char_id
		}
    return render_to_response(
		'chargen/basics.html', 
		RequestContext(request, context)
		)
    
@login_required
def assignstats(request, char_id, stat_string):
	"""
	Receive the user's input for which number values 
	to assign to which stats.
	"""
    character = models.Character.objects.get(id=char_id)
    number_of_stats = models.Stat.objects.count()
    i = 0
    vals = stat_string.split("_")[0:number_of_stats]
    for stat in models.Stat.objects.all():
        character.stats.create(name=stat, value=vals[i])
        character.save()
        i += 1
    return HttpResponseRedirect('/cg/basics/' + str(char_id))
       
@login_required        
def delete(request, char_id):
    character = models.Character.objects.get(id=char_id)
    character.delete()
    return HttpResponseRedirect('/cg/list')
    
@login_required
def classpage(request, char_id):
    character = models.Character.objects.get(id=char_id)
    next_page = character.cls.name
    return HttpResponseRedirect('/cg/' + next_page + "/" + char_id)
    
@login_required        
def mage(request, char_id):
	"""
	Prepare/handle a form with options suited to a character who is the 
	Mage class. For /mage url.
	"""
    character = models.Character.objects.get(id=char_id)
    character.hp = 4
    char_int = character.stats.get(name=7)
    int_stat = char_int.name
    int_mods = int_stat.ability_modifiers
    int_lang_mods = int_mods.filter(name__exact="lang")
    int_lang_mod_for_val = int_lang_mods.get(
		stat_value__exact=char_int.value
		)
    number_of_langs = int(int_lang_mod_for_val.mod_value)
    character.number_of_spells = number_of_langs + 2
    character.save()
    weapon_choices = []
    for weapon in models.Weapon.objects.all():
        weapon_choice = (weapon.id, weapon.name)
        if character.cls.name in weapon.allowed_classes:
            weapon_choices.append(weapon_choice)
    spell_choices = []
    for spell in models.Spell.objects.all():
        spell_choice = (spell.id, spell.name)
        spell_choices.append(spell_choice)
    class MageForm(forms.Form):
        spells = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple(),
            choices=spell_choices,
            label="Spells (choose " + \
				str(character.number_of_spells) + ")"
				)
        proficiencies = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple(),
            choices=weapon_choices,
            label="Weapon Proficiencies (choose 2)"
            )
    skill_message = 
		"Based on your Intellegence, \
		you are allowed to choose up to " + \
        str(character.number_of_spells) + " spells from this list."
    proficiency_message = 
		"Mages choose two weapons in which to be proficient."

    if request.method == 'POST': # If the form has been submitted...
        form = MageForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            spells = form.cleaned_data['spells']
            weapons = form.cleaned_data['proficiencies']
            for spell in spells:
                s = models.Spell.objects.get(id=int(spell))
                character.spells.add(s)
            for weapon in weapons:
                w = models.Weapon.objects.get(id=int(weapon))
                character.weapons.add(w)
            character.save()
            return HttpResponseRedirect('/cg/view/' + str(char_id))
        else:
            form = MageForm() # An unbound form
            form_message = """The values were not valid. \
				Be sure to choose at least one spell and \
				one weapon proficiency."""
    else:
        form = MageForm() # An unbound form
        form_message = ""
    context = {'form':form, 
        "skill_message":skill_message,
         "proficiency_message":proficiency_message,
         "form_message":form_message,
        "character":character}
    return render_to_response(
		'chargen/classpage.html', 
		RequestContext(request, context)
		)
    
@login_required        
def thief(request, char_id):
	"""
	Prepare/handle a form with options suited to a character who is the 
	Thief class. For /thief url.
	"""
    character = models.Character.objects.get(id=char_id)
    character.hp = 6
    character.save()
    weapon_choices = []
    for weapon in models.Weapon.objects.all():
        weapon_choice = (weapon.id, weapon.name)
        if character.cls.name in weapon.allowed_classes:
            weapon_choices.append(weapon_choice)
    skill_choices = []
    for skill in models.Skill.objects.all():
        skill_choice = {'id':skill.id, 
            'name':skill.name,
            'initial':skill.initial_value}
        skill_choices.append(skill_choice)
        
    class ThiefForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(ThiefForm, self).__init__(*args, **kwargs)
            
            for skill_choice in skill_choices:
                label=skill_choice['name'] + \
					" (intial value " + \
					str(skill_choice['initial']) + ")"
                self.fields["skill_" + str(skill_choice['id'])] = 
					forms.IntegerField(label=label)
                
        proficiencies = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple(),
            choices=weapon_choices,
            label="Weapon Proficiencies (choose 3)"
            )
        
    skill_message = """Thieves have skill 60 points to distribute. \
		The thief skills are listed below with their initial values. \
		The points you distribute to these skills will be added to \
		the initial values. You must enter a value in every skill slot. \ 
		You may enter 0."""
    proficiency_message = 
		"Thieves choose three weapons in which to be proficient."
    if request.method == 'POST': # If the form has been submitted...
        form = ThiefForm(request.POST) # A form bound to the POST data
        logging.info(str(request.POST))
        if form.is_valid(): # All validation rules pass
            weapons = form.cleaned_data['proficiencies']
            for weapon in weapons:
                w = models.Weapon.objects.get(id=int(weapon))
                character.weapons.add(w)
            
            for skill_choice in skill_choices:
                logging.info(
					"skill_choice['name']: " + skill_choice['name'])
                skill_entry = 
					form.cleaned_data["skill_" + str(skill_choice['id'])]
                skill_value = skill_entry + skill_choice['initial']
                cs = models.CharSkill(
					name=skill_choice['name'], 
                    value=skill_value
                    )
                cs.save()
                character.skills.add(cs)
            character.save()
            return HttpResponseRedirect('/cg/view/' + str(char_id))
        else:
            form = ThiefForm() # An unbound form
            form_message = """The values were not valid. \
				Be sure to enter a value on every skill, \
				even if it is 0, and choose at least one \
				weapon proficiency."""
    else:
        form = ThiefForm() # An unbound form
        form_message = ""
        
    context = {'form':form, 
        "skill_message":skill_message,
         "proficiency_message":proficiency_message,
         "form_message":form_message,
        "character":character}
    return render_to_response(
		'chargen/classpage.html', 
		RequestContext(request, context)
		)
    
@login_required        
def fighter(request, char_id):
	"""
	Prepare/handle a form with options suited to a character who is the 
	Fighter class. For /fighter url.
	"""
    character = models.Character.objects.get(id=char_id)
    character.hp = 10
    character.save()
    weapon_choices = []
    for weapon in models.Weapon.objects.all():
        weapon_choice = (weapon.id, weapon.name)
        if character.cls.name in weapon.allowed_classes:
            weapon_choices.append(weapon_choice)
    spell_choices = []
    for spell in models.Spell.objects.all():
        spell_choice = (spell.id, spell.name)
        spell_choices.append(spell_choice)
    class FighterForm(forms.Form):
        proficiencies = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple(),
            choices=weapon_choices,
            label="Weapon Proficiencies (choose 4)"
            )
    skill_message = "Fighters have no additional skills to choose."
    proficiency_message = 
		"Fighters choose four weapons in which to be proficient."
    if request.method == 'POST': # If the form has been submitted...
        form = FighterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            weapons = form.cleaned_data['proficiencies']
            for weapon in weapons:
                w = models.Weapon.objects.get(id=int(weapon))
                character.weapons.add(w)
            character.save()
            return HttpResponseRedirect('/cg/view/' + str(char_id))
        else:
            form = FighterForm() # An unbound form
            form_message = """The values were not valid. \
            Be sure to choose at least one weapon proficiency."""
    else:
        form = FighterForm() # An unbound form
        form_message = ""
        
    context = {'form':form, 
        "skill_message":skill_message,
         "proficiency_message":proficiency_message,
         "form_message":form_message,
        "character":character}
    return render_to_response(
		'chargen/classpage.html', 
		RequestContext(request, context)
		)
    
@login_required        
def cleric(request, char_id):
	"""
	Prepare/handle a form with options suited to a character who is the 
	Cleric class. For /cleric url.
	"""
    character = models.Character.objects.get(id=char_id)
    character.hp = 8
    character.save()
    weapon_choices = []
    for weapon in models.Weapon.objects.all():
        weapon_choice = (weapon.id, weapon.name)
        if character.cls.name in weapon.allowed_classes:
            weapon_choices.append(weapon_choice)
    spell_choices = []
    for spell in models.Spell.objects.all():
        spell_choice = (spell.id, spell.name)
        spell_choices.append(spell_choice)
    class ClericForm(forms.Form):
        proficiencies = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple(),
            choices=weapon_choices,
            label="Weapon Proficiencies (choose 3)")
    skill_message = """Clerics have access to all first level Cleric \
		spells. You do not need to choose spells."""
    proficiency_message = 
		"Clerics choose three weapons in which to be proficient."
    if request.method == 'POST': # If the form has been submitted...
        form = ClericForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            weapons = form.cleaned_data['proficiencies']
            for weapon in weapons:
                w = models.Weapon.objects.get(id=int(weapon))
                character.weapons.add(w)
            character.save()
            return HttpResponseRedirect('/cg/view/' + str(char_id))
        else:
            form = ClericForm() # An unbound form
            form_message = "The values were not valid. \
				Be sure to choose at least one weapon proficiency."
    else:
        form = ClericForm() # An unbound form
        form_message = ""
        
    context = {'form':form, 
        "skill_message":skill_message,
        "form_message":form_message,
         "proficiency_message":proficiency_message,
        "character":character}
    return render_to_response('chargen/classpage.html', RequestContext(request, context))
    
    
    
    
    
