from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

#
# resnet_internal orientation ajax methods
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

@dajaxice_register
def complete_task(request, username, task):
    dajax = Dajax()

    user = get_user_model().objects.get(username=username)

    if task == "onity":
        user.onity_complete = True
    elif task == "srs":
        user.srs_complete = True
    elif task == "payroll":
        user.payroll_complete = True

    user.save()

    dajax.redirect(reverse('orientation-checklist'))

    return dajax.json()

@dajaxice_register
def complete_orientation(request, username):
    dajax = Dajax()

    user = get_user_model().objects.get(username=username)
    user.orientation_complete = True
    user.is_new_tech = False
    user.save()

    dajax.redirect(reverse('logout'))

    return dajax.json()
