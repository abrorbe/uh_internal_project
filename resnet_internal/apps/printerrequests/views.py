"""
.. module:: reslife_internal.printerrequests.views
   :synopsis: ResLife Internal Printer Request Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime
import logging

from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from srsconnector.models import PrinterRequest

from ...settings.base import DAILY_DUTIES_ACCESS
from ..core.models import CSDMapping
from .forms import TonerCountForm, PartCountForm, TonerRequestForm, PartsRequestForm
from .models import Request, Toner, Part


logger = logging.getLogger(__name__)

SERVICE_REQUEST_TYPE_MAP = {
    "toner": '**TONER_REQUEST',
    "parts": '**PARTS_REQUEST',
}


class PrinterRequestMixin(object):
    success_url = reverse_lazy('printerrequests')

    def create_requests(self, priority, request_type, for_front_desk, printer, request_list, user):
        # Create the service request
        service_request = PrinterRequest()
        service_request.priority = priority
        service_request.requestor_username = user.username
        service_request.printer_model = printer.model
        service_request.printer_manufacturer = printer.make
        service_request.request_type = SERVICE_REQUEST_TYPE_MAP[request_type]
        service_request.request_list = request_list
        service_request.work_log = 'Created Ticket for {full_name} ({email})'.format(user.get_full_name(), user.username)
        service_request.save()

        # Create the printer request.
        printer_request = Request()
        printer_request.ticket_id = service_request.ticket_id
        printer_request.date_requested = datetime.now()
        printer_request.priority = priority
        printer_request.requestor = user.username

        # Determine where to send it
        try:
            address = CSDMapping.objects.get(email=user.username).domain + " " + ("Front Desk" if for_front_desk else "CSD Office")
        except CSDMapping.DoesNotExist:
            updated_toner_service_request = PrinterRequest.objects.get(ticket_id=service_request.ticket_id)
            address = "Building " + updated_toner_service_request.requestor_building + " Room " + updated_toner_service_request.requestor_room

        printer_request.address = address
        printer_request.status = Request.STATUSES.index("Open")

        printer_request.save()

        getattr(printer_request, request_type).add(*request_list)


class RequestTonerView(PrinterRequestMixin, FormView):
    """Creates a service request for printer toner."""

    template_name = "printerrequests/request_toner.djhtml"
    form_class = TonerRequestForm

    def form_valid(self, form):
        priority = form.cleaned_data['priority']
        printer = form.cleaned_data['printer']  # Returns a printer object, since ModelChoiceField was used
        toner_id = form.cleaned_data['toner']
        for_front_desk = form.cleaned_data['for_front_desk']

        toner = Toner.objects.get(id=toner_id)
        request_list = [toner]

        self.create_requests(priority=priority, request_type='toner', for_front_desk=for_front_desk, printer=printer, request_list=request_list, user=self.request.user)

        return super().form_valid(form)


class RequestPartsView(PrinterRequestMixin, FormView):
    """Creates a service request for printer parts."""

    template_name = "printerrequests/request_part.djhtml"
    form_class = PartsRequestForm

    def form_valid(self, form):
        priority = form.cleaned_data['priority']
        printer = form.cleaned_data['printer']  # Returns a printer object, since ModelChoiceField was used
        part_id = form.cleaned_data['part']

        part = Part.objects.get(id=part_id)
        request_list = [part]

        self.create_requests(priority=priority, request_type='parts', for_front_desk=False, printer=printer, request_list=request_list, user=self.request.user)

        return super().form_valid(form)


class RequestsListView(ListView):
    """Lists all open printer requests and supplies a form to modify the request status."""

    template_name = "printerrequests/viewrequests.djhtml"

    def get_queryset(self):
        query = Request.objects.exclude(status=Request.STATUSES.index('Delivered'))

        # Only show all requests if the user has access to fulfill them
        if not self.request.user.has_access(DAILY_DUTIES_ACCESS):
            query = query.filter(requestor=self.request.user.get_alias())

        return query


class InventoryView(TemplateView):
    """Lists inventory for both parts and toner."""

    template_name = "printerrequests/viewinventory.djhtml"
    toner_form = TonerCountForm
    part_form = PartCountForm

    def get_context_data(self, **kwargs):
        context = super(InventoryView, self).get_context_data(**kwargs)

        toner_list = []
        part_list = []

        # Build the toner inventory
        for cartridge in Toner.objects.all():
            list_object = {}
            list_object['cartridge'] = cartridge
            list_object['count_form'] = self.toner_form(instance=cartridge)

            toner_list.append(list_object)

        # Build the part inventory
        for part in Part.objects.all():
            list_object = {}
            list_object['part'] = part
            list_object['count_form'] = self.part_form(instance=part)

            part_list.append(list_object)

        context['toner_list'] = toner_list
        context['part_list'] = part_list

        return context


class OnOrderView(InventoryView):
    """Lists order counts for both parts and toner."""

    template_name = "printerrequests/viewordered.djhtml"
