"""
.. module:: resnet_internal.apps.printerrequests.ajax
   :synopsis: University Housing Internal Printer Request AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import logging

from clever_selects.views import ChainedSelectChoicesView
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax
from srsconnector.models import STATUS_CHOICES, PrinterRequest

from .models import Request, Toner, Part
from .utils import can_fulfill_request, send_replenishment_email, send_delivery_confirmation


logger = logging.getLogger(__name__)


class TonerChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Toner.objects.filter(printer__id=self.parent_value).order_by('color')


class PartChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Part.objects.filter(printer__id=self.parent_value).order_by('type')


@ajax
@require_POST
def change_request_status(request):
    """ Updates the status of a printer request based on a drop-down value.

    :param request_id: The id of the request to process.
    :type request_id: str
    :param current_status: The new status value.
    :type status: str

    """

    # Pull post parameters
    request_id = request.POST["request_id"]
    current_status = request.POST["current_status"]

    context = {}
    context["success"] = True
    context["error_message"] = None

    send_replenishment_email()

    status = int(current_status) + 1

    STATUS_MAP = {
        Request.STATUSES.index('Acknowledged'): 'Work In Progress',
        Request.STATUSES.index('Delivered'): 'Closed',
    }

    request_instance = Request.objects.get(id=request_id)

    if status in STATUS_MAP:
        # Handle inventory decrementation for acknowledge requests
        if status == Request.STATUSES.index('Acknowledged'):
            if can_fulfill_request(request_id):
                # Decrement each cartridge quantity
                for cartridge in request_instance.toner.all():
                    cartridge.quantity = cartridge.quantity - 1
                    cartridge.save()

                # Decrement each part quantity
                for part in request_instance.parts.all():
                    part.quantity = part.quantity - 1
                    part.save()
            else:
                context["success"] = False
                context["error_message"] = "Cannot acknowledge request: Insufficient Inventory."
                return context

        # Update the SRS ticket
        ticket = PrinterRequest.objects.get(ticket_id=request_instance.ticket_id)

        # Grab the correct value for the srs ticket status
        ticket_status = STATUS_MAP[status]
        for choice in STATUS_CHOICES:
            if ticket_status in choice:
                srs_status_value = choice[1]  # The status won't accept the int values

        ticket.status = srs_status_value

        if status == Request.STATUSES.index('Delivered'):
            ticket.solution = "Item delivered by %s." % request.user.get_full_name()
            send_delivery_confirmation(request_instance)

        request_list = []

        if "TONER" in ticket.request_type:
            for cartridge in request_instance.toner.all():
                request_list.append(cartridge)
        elif "PARTS" in ticket.request_type:
            for part in request_instance.parts.all():
                request_list.append(part)

        ticket.request_list = request_list  # Must include in update; gets blanked otherwise
        ticket.work_log = "Ticket status updated to %s by %s." % (Request.STATUSES[status], request.user.get_full_name())
        ticket.save()

    request_instance.status = status
    request_instance.save()

    return HttpResponseRedirect(reverse('printerrequests:home'))


@ajax
@require_POST
def update_toner_inventory(request):
    """ Updates the inventory quantity of a toner cartridge.

    :param toner_id: The id of the toner cartridge to process.
    :type toner_id: str
    :param quantity: The updated quantity.
    :type quantity: str
    :param ordered: The updated order count.
    :type ordered: str

    """

    # Pull post parameters
    toner_id = request.POST["toner_id"]
    quantity = request.POST.get("quantity", None)
    ordered = request.POST.get("ordered", None)

    toner_instance = Toner.objects.get(id=toner_id)
    if quantity:
        toner_instance.quantity = int(quantity)
    if ordered:
        toner_instance.ordered = int(ordered)
    toner_instance.save()


@ajax
@require_POST
def update_part_inventory(request):
    """ Updates the inventory quantity of a printer part.

    :param part_id: The id of the toner cartridge to process.
    :type part_id: str
    :param quantity: The updated quantity.
    :type quantity: str
    :param ordered: The updated order count.
    :type ordered: str

    """

    # Pull post parameters
    part_id = request.POST["part_id"]
    quantity = request.POST.get("quantity", None)
    ordered = request.POST.get("ordered", None)

    part_instance = Part.objects.get(id=part_id)
    if quantity:
        part_instance.quantity = int(quantity)
    if ordered:
        part_instance.ordered = int(ordered)
    part_instance.save()
