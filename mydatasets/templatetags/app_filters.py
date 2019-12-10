from django import template
register = template.Library()

from mydatasets.models import (BrainRegion3, CellType3)
from django.contrib.auth.models import Group

@register.filter
def to_int(value):
    if type(value) is list:
        cast_list = []
        for element in value:
            cast_list.append(int(element))
        return cast_list
    return int(value)

@register.filter
def to_str(value):
    return str(value)


@register.filter
def correct_media(value):
    address = str(value)
    # return value
    # if type(value) == 'String':
    return address.replace("/media/media/", "/media/")
    # return value

def xstr(s):
    if s is None:
        return ''
    return str(s)

@register.filter
def check_new_values(item):
    new_item = xstr(item.new_development_stage) + xstr(item.new_species) + xstr(item.new_strain) + xstr(item.new_gender) + xstr(item.new_age_type) + xstr(item.new_brain_region1) + xstr(item.new_brain_region2) + xstr(item.new_brain_region3) + xstr(item.new_cell_type1) + xstr(item.new_cell_type2) + xstr(item.new_cell_type3) + xstr(item.new_experimental_condition) + xstr(item.new_experimental_protocol) + xstr(item.new_stain) + xstr(item.new_slicing_direction) + xstr(item.new_reconstruction_software) + xstr(item.new_objective_type) + xstr(item.new_data_type) + xstr(item.new_objective_magnification)
    # new_item = new_item = (item.new_species) or (item.new_strain) or (item.new_gender) or (item.new_age_type) or (item.new_brain_region1) or (item.new_brain_region2) or (item.new_brain_region3) or (item.new_cell_type1) or (item.new_cell_type2) or (item.new_cell_type3) or (item.new_experimental_condition) or (item.new_experimental_protocol) or (item.new_stain) or (item.new_slicing_direction) or (item.new_reconstruction_software) or (item.new_objective_type) or (item.new_data_type)
    new_item = " ".join(new_item.split())
    if len(new_item.strip()) >= 1:
        # print len(new_item), new_item
        return True
    return False

@register.filter
def cell_count(archive):
    cells = 0
    for grp in archive:
        cells += int(grp.number_of_data_files or 0)
    return cells

@register.filter
def brainregion3_get(id):
    try:
        if id == None or id == "" or id == 'None':
            return ""
        return BrainRegion3.objects.get(id=int(id))
    except:
        print "Error with finding brain region 3"
        return ""

@register.filter
def celltype3_get(id):
    try:
        if id == None or id == "" or id == 'None':
            return ""
        return CellType3.objects.get(id=int(id))
        # return BrainRegion3.objects.get(id=int(id))
    except:
        print "Error with finding celltype3"
        return ""

@register.filter
def get_item(dictionary, key):
    # print dictionary, key
    return dictionary.get(str(key))

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(is_safe=False)
def my_default_if_none(value, arg):
    """If value is None, use given default."""
    if value is None or str(value).strip() is '':
        return arg
    return str(value) + '/'