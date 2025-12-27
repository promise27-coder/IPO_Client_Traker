from django.shortcuts import render, get_object_or_404, redirect
from .models import IPO, ClientApp, MasterClient
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

# --- FORMS CONFIGURATION ---
ClientForm = modelform_factory(ClientApp, exclude=['owner', 'profit_share_45', 'ipo'])
IPOForm = modelform_factory(IPO, fields=['name', 'active'])
MasterForm = modelform_factory(MasterClient, exclude=['owner'])

# --- VIEWS ---

# 1. Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

# 2. UPDATED DASHBOARD (Main Page)
@login_required(login_url='login')
def dashboard(request):
    ipos = IPO.objects.filter(active=True)
    selected_ipo_id = request.GET.get('ipo_id')
    
    # Master List fetch karo (Main page par batava mate)
    masters = MasterClient.objects.filter(owner=request.user)
    
    if selected_ipo_id:
        current_ipo = get_object_or_404(IPO, id=selected_ipo_id)
        clients = ClientApp.objects.filter(owner=request.user, ipo=current_ipo)
    else:
        current_ipo = None
        clients = []

    return render(request, 'core/dashboard.html', {
        'ipos': ipos, 
        'current_ipo': current_ipo, 
        'clients': clients,
        'masters': masters,        # <-- Master List Data
        'master_form': MasterForm() # <-- Quick Add Form
    })

# 3. Add Client (Manual Add Row)
@login_required(login_url='login')
def add_client(request):
    ipo_id = request.GET.get('ipo_id')
    if not ipo_id: return redirect('dashboard')
    ipo_obj = get_object_or_404(IPO, id=ipo_id)

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.ipo = ipo_obj
            client.save()
            return redirect(f'/?ipo_id={ipo_id}')
    else:
        form = ClientForm()
    return render(request, 'core/form.html', {'form': form, 'title': f'Add to {ipo_obj.name}'})

# 4. Detail View (For Manual Full Edit)
@login_required(login_url='login')
def client_detail(request, id):
    client = get_object_or_404(ClientApp, id=id, owner=request.user)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect(f'/?ipo_id={client.ipo.id}')
    else:
        form = ClientForm(instance=client)
    return render(request, 'core/form.html', {'form': form, 'title': f'Edit: {client.nickname}'})

# 5. NEW: Quick Add Master Logic (Dashboard mathi j add karva)
@login_required
def add_master_entry(request):
    if request.method == "POST":
        form = MasterForm(request.POST)
        if form.is_valid():
            master = form.save(commit=False)
            master.owner = request.user
            master.save()
    return redirect('dashboard')

# 6. Add IPO View
@login_required(login_url='login')
def add_ipo(request):
    if request.method == "POST":
        form = IPOForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = IPOForm()
    return render(request, 'core/form.html', {'form': form, 'title': '🚀 Create New IPO'})

# 7. Import from Master to IPO
@login_required(login_url='login')
def import_from_master(request, ipo_id):
    ipo_obj = get_object_or_404(IPO, id=ipo_id)
    existing_nicknames = ClientApp.objects.filter(ipo=ipo_obj, owner=request.user).values_list('nickname', flat=True)
    masters = MasterClient.objects.filter(owner=request.user).exclude(nickname__in=existing_nicknames)

    if request.method == "POST":
        selected_ids = request.POST.getlist('master_ids')
        for m_id in selected_ids:
            master = MasterClient.objects.get(id=m_id)
            ClientApp.objects.create(
                owner=request.user,
                ipo=ipo_obj,
                nickname=master.nickname,
                broker=master.broker,
                demat_acc=master.demat_acc,
                pan_number=master.pan_number,
                is_applied=True
            )
        return redirect(f'/?ipo_id={ipo_id}')

    return render(request, 'core/import_clients.html', {'masters': masters, 'ipo': ipo_obj})

# 8. Manage Master List (Dedicated Page - Optional now)
@login_required(login_url='login')
def manage_master(request):
    masters = MasterClient.objects.filter(owner=request.user)
    if request.method == "POST":
        form = MasterForm(request.POST)
        if form.is_valid():
            master = form.save(commit=False)
            master.owner = request.user
            master.save()
            return redirect('manage_master')
    else:
        form = MasterForm()
    return render(request, 'core/master_list.html', {'masters': masters, 'form': form})

# 9. AUTO-SAVE: Update Client Cell (IPO Table)
@login_required
def update_client_cell(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        client = get_object_or_404(ClientApp, id=id, owner=request.user)
        
        field_name = data.get('field')
        value = data.get('value')

        if hasattr(client, field_name):
            if field_name in ['is_applied', 'upi_request_sent', 'payment_cleared', 'payout_done', 'screenshot_sent']:
                value = True if value else False
            
            if field_name == 'total_profit':
                if value == '': value = 0
                
            setattr(client, field_name, value)
            client.save()
            
            return JsonResponse({
                'status': 'success', 
                'profit_share_45': client.profit_share_45
            })
            
    return JsonResponse({'status': 'error'}, status=400)

# 10. AUTO-SAVE: Update Master Cell (Master Table)
@login_required
def update_master_cell(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        master = get_object_or_404(MasterClient, id=id, owner=request.user)
        
        field_name = data.get('field')
        value = data.get('value')

        if hasattr(master, field_name):
            setattr(master, field_name, value)
            master.save()
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400)