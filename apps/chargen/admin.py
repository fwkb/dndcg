from django.contrib import admin

from chargen.models import *

#Register models so they will show up in the admin interface.

admin.site.register(Character)
admin.site.register(CharacterStat)
admin.site.register(Stat)
admin.site.register(Race)
admin.site.register(StatModifier)
admin.site.register(StatMinimum)
admin.site.register(StatMaximum)
admin.site.register(Posession)
admin.site.register(Weapon)
admin.site.register(Cls)
admin.site.register(RacialAbility)
admin.site.register(ClassAbility)
admin.site.register(AbilityModifier)
admin.site.register(Details)
admin.site.register(Proficiency)
admin.site.register(Spell)
admin.site.register(Skill)
admin.site.register(CharSkill)


