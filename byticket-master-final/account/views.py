
from django.shortcuts import render_to_response, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .serializers import SeatSerializer, OrderSerializer
from .form import Register_form, Login_form
from django.contrib.auth.hashers import make_password, check_password
from Bytickey.settings import logger
from .models import myUser
from django.template import RequestContext
from .models import myUser
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from .models import order, user_seat_selection, seat
from django.db.models import Q
from time import strftime, localtime
import json


def login(request):
    if request.method == "GET":
        return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))
    elif request.method == 'POST':
        # Character length must be met
        User_form = Login_form(request.POST)
        if User_form.is_valid():
            username = User_form.cleaned_data.get('username')
            password = User_form.cleaned_data.get('password')
            data = myUser.objects.filter(username=username)
            # Verification
            if data:
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return render_to_response('accounts/index.html', locals(), content_type=RequestContext(request))
                else:
                    return HttpResponse('Invalid Credientials', status=401)
            else:
                logger.info('username is not exits!')
                error = 'username is not exits,please check your name'
                return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))
        else:
            logger.info('login failed ,username or password is error')
            error = 'please check your password or username'
            return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))


def register(request):
    if request.method == 'GET':
        return render_to_response('accounts/register.html', locals(), content_type=RequestContext(request))
    elif request.method == 'POST':
        logger.info(request.POST)
        # Character length must be met
        User_form = Register_form(request.POST)
        if User_form.is_valid():
            username = User_form.cleaned_data.get('username')
            password = User_form.cleaned_data.get('password')
            email = User_form.cleaned_data.get('email')
            try:
                myUser.objects.get(username=username)
                logger.info("username is exits")
                error = '2'
                return render_to_response('accounts/register.html', locals(), content_type=RequestContext(request))
            except:
                myUser.objects.create_user(username=username, password=password, email=email)
                return HttpResponseRedirect('/accounts/login/')
        else:
            logger.info('register failed')
            render_to_response('accounts/register.html', locals(), content_type=RequestContext(request))
    else:
        return HttpResponse('ERROR')


def loginout(request):
    # clean flush
    request.session.flush()
    return redirect(reverse('login'))


@login_required
def user_setting(request):
    user = request.user
    userid = myUser.objects.get(username=user).id
    if request.method == 'GET':
        query = myUser.objects.get(id=userid)
        return render_to_response('accounts/AccountSetting.html', locals(), content_type=RequestContext(request))
    if request.method == 'POST':
        # update the personal information
        num = request.POST.get('luggage')
        preferred = request.POST.get('project_id')
        full_name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            myUser.objects.filter(username=request.user).update(number_luggage=num,
                                                                prefered=preferred,
                                                                first_name=full_name,
                                                                email=email,
                                                                password=make_password(password),
                                                                )
            request.session.flush()
            return redirect(reverse('login'))
        except Exception as e:
            logger.info('account is not exits!,error information{}'.format(e))
        return render_to_response('accounts/AccountSetting.html', locals(), content_type=RequestContext(request))


@login_required
def add_Ticket(request):
    if request.method == 'GET':
        return render_to_response('accounts/AddTicket.html', locals(), content_type=RequestContext(request))
    if request.method == 'POST':
        data = myUser.objects.get(username=request.user)
        passwd = request.POST.get('password')
        try:
            # Verify both the order key and the user
            order.objects.get(order_key=passwd, user_name_id=data.id)
            return HttpResponseRedirect('/accounts/seat_selection/?id={}'.format(passwd))
        except:
            error = 'error'
            return render_to_response('accounts/AddTicket.html', locals(), content_type=RequestContext(request))


@login_required
def seat_selection(request):
    global query_info
    if request.method == 'GET':
        data = myUser.objects.get(username=request.user)
        order_key = request.GET.get('id')
        # Show all order information
        query = order.objects.get(order_key=order_key, user_name_id=data.id)
        return render_to_response('accounts/Seat_Selection.html', locals(), content_type=RequestContext(request))
    if request.method == 'POST':
        seat_id = request.POST.getlist('id', None)
        ticket = request.POST.get('ticket')
        delete_id = request.POST.get('delete_id')
        order_number = request.POST.get('order_number')
        query_data = myUser.objects.get(username=request.user)
        logger.info('The seat number obtained is{}'.format(seat_id))
        logger.info('Cancel seat number ID is{}'.format(delete_id))
        logger.info('Get the order number{}'.format(order_number))
        userinfo = myUser.objects.get(username=request.user)
        if delete_id and request.POST.get('ticket') == 'Ticket1' and delete_id != "":
            name_id = myUser.objects.get(username=request.user)
            seat.objects.get(seat_number=delete_id, seat_type='1', name_id_id=name_id.id).delete()
        elif delete_id and request.POST.get('ticket') == 'Ticket2' and delete_id != "":
            name_id = myUser.objects.get(username=request.user)
            seat.objects.get(seat_number=delete_id, seat_type='2', name_id_id=name_id.id).delete()
        if order_number:
            query_info = order.objects.get(user_name=userinfo.id, order_number=order_number)
        else:
            logger.info('order number does not exist')
        if len(seat.objects.filter(Q(name_id=query_data.id) & Q(seat_type=1))) >= int(query_info.seat_number):
            logger.info('Please select a new seat if the number of seats is exceeded')
            return JsonResponse({'status': '1', 'error': 'Please re-select if the number of seats is exceeded'})
        # insert data
        if request.POST.get('ticket') == 'Ticket1' and seat_id != "":
            # Handling special cases: different users occupy different time periods
            name_id = myUser.objects.get(username=request.user)
            try:
                seat.objects.get(seat_type='1', name_id_id=name_id.id, seat_number=seat_id[0],
                                 order_id_id=query_info.id)
                return JsonResponse({'status': '1', 'error': 'The seat number already exists and cannot be created '
                                                             'repeatedly '})
            except:
                # Create seat selection
                num = seat.objects.update_or_create(seat_type='1', name_id_id=name_id.id, seat_number=seat_id[0],
                                                    seat_status='2',
                                                    order_id_id=query_info.id,
                                                    seat_complete_time=strftime('%Y-%m-%d %H:%M:%S', localtime()))
        elif request.POST.get('ticket') == 'Ticket2' and seat_id != "":
            name_id = myUser.objects.get(username=request.user)
            try:
                seat.objects.get(seat_type='2', name_id_id=name_id.id, seat_number=seat_id[0],
                                 order_id_id=query_info.id)
                return JsonResponse({'status': '1', 'error': 'The seat number already exists and cannot be created '
                                                             'repeatedly'})
            except:
                # Create seat selection
                num = seat.objects.update_or_create(seat_type='2', name_id_id=name_id.id, seat_number=seat_id[0],
                                                    seat_status='2',
                                                    order_id_id=query_info.id,
                                                    seat_complete_time=strftime('%Y-%m-%d %H:%M:%S', localtime()))
        return HttpResponseRedirect('/accounts/booking_display/')


@login_required
def booking_display(request):
    data = myUser.objects.get(username=request.user)
    order_key = request.GET.get('id')
    # Show all order information
    query = order.objects.get(user_name_id=data.id, order_key=order_key)
    return render_to_response('accounts/Booking_display.html', locals(), content_type=RequestContext(request))

# Administrator verification
def manage(request):
    if request.method == 'GET':
        manage = '1'
        return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))
    else:
        User_form = Login_form(request.POST)
        if User_form.is_valid():
            username = User_form.cleaned_data.get('username')
            password = User_form.cleaned_data.get('password')
            data = myUser.objects.filter(username=username)
            if data:
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return HttpResponseRedirect('/accounts/manage_do/')
                else:
                    return HttpResponse('Invalid Credientials', status=401)
            else:
                logger.info('username is not exits!')
                error = 'username is not exits,please check your name'
                return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))
        else:
            logger.info('login failed ,username or password is error')
            error = 'please check your password or username'
            return render_to_response('accounts/login.html', locals(), content_type=RequestContext(request))

# Administrator Operations
def manage_do(request):
    if request.method == 'GET':
        return render_to_response('accounts/seat_adjustment.html', locals(), content_type=RequestContext(request))
    if request.method == 'POST':
        seat_number = request.POST.get('id')
        seat_sid_add = request.POST.get('seat_id_add')
        seat_sid_delete = request.POST.get('seat_id_delete')
        query = myUser.objects.get(username=request.user)
        # Delete booking
        if seat_number:
            seat.objects.get(seat_number=seat_number).delete()
        # Freezing seats
        if seat_sid_add:
            seat.objects.update_or_create(seat_type=1, seat_number=seat_sid_add, seat_status=1, name_id_id=query.id,
                                          seat_complete_time=strftime('%Y-%m-%d %H:%M:%S', localtime()))
        # Unfreezing seats
        if seat_sid_delete:
            seat.objects.get(seat_number=seat_sid_delete).delete()
        return render_to_response('accounts/seat_adjustment.html', locals(), content_type=RequestContext(request))


def modal_data_select(request):
    # Fetch data for display in the manager interface
    seat_sid_select = request.POST.get('seat_id_select')
    seat_data = seat.objects.get(seat_number=seat_sid_select)
    return JsonResponse({'username': seat_data.name_id_id, 'seat_complete_time': seat_data.seat_complete_time,
                         'seat_number': seat_data.seat_number,
                         'ticket_type': seat_data.seat_type})


class SeatView(viewsets.ModelViewSet):
    queryset = seat.objects.all()
    serializer_class = SeatSerializer


class OrderView(viewsets.ModelViewSet):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
