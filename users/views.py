from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .forms import ClientForm, ItemForm, InvoiceForm 
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum
from .models import Client, Item, Invoice
from django.core.mail import EmailMessage
from .models import Invoice
from django.template.loader import render_to_string
from io import BytesIO 



def home(request):
    return HttpResponse("Hello! This is the Users app working.")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # create new user
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')   # after signup go to login page
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # redirect to dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')
def dashboard(request):
    total_clients = Client.objects.count()
    total_items = Item.objects.count()
    total_invoices = Invoice.objects.count()
    total_paid = Invoice.objects.filter(is_paid=True).count()
    total_unpaid = Invoice.objects.filter(is_paid=False).count()
    
    context = {
        'total_clients': total_clients,
        'total_items': total_items,
        'total_invoices': total_invoices,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')
def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ClientForm()
    return render(request, 'add_client.html', {'form': form})

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})
@login_required
def add_invoice(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)  # Save instance without committing m2m
            invoice.save()  # Save invoice first
            invoice.items.set(form.cleaned_data['items'])  # Assign ManyToMany manually
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'add_invoice.html', {'form': form})
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoice_detail.html', {'invoice': invoice})
@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    
    # Search by client name
    query = request.GET.get('q')
    if query:
        invoices = invoices.filter(client__name__icontains=query)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'paid':
        invoices = invoices.filter(is_paid=True)
    elif status == 'unpaid':
        invoices = invoices.filter(is_paid=False)
    
    return render(request, 'invoice_list.html', {'invoices': invoices})
@login_required
def invoice_detail(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    items = invoice.items.all()  # related_name='items' in InvoiceItem
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'items': items})

def invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    items = invoice.items.all()
    
    template_path = 'invoice_pdf.html'
    context = {'invoice': invoice, 'items': items}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice_{invoice.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response
@login_required
def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    
    # Render the template
    return render(request, 'edit_client.html', {'form': form})
@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.price = request.POST.get('price')
        item.save()
        return redirect('item_list')

    return render(request, 'edit_item.html', {'item': item})
@login_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'edit_invoice.html', {'form': form})
@login_required
def delete_client(request, client_id):
    client = Client.objects.get(id=client_id)
    client.delete()
    return redirect('dashboard')

@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    item.delete()
    return redirect('dashboard')

@login_required
def delete_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.delete()
    return redirect('invoice_list')
@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'client_list.html', {'clients': clients})

@login_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})


def send_invoice_email(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Calculate total
    total = sum([item.price for item in invoice.items.all()])

    # Render HTML
    html = render_to_string('invoice_pdf.html', {'invoice': invoice, 'total': total})

    # Generate PDF
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)
    pdf_file.seek(0)

    # Prepare email
    email = EmailMessage(
        subject=f'Invoice #{invoice.id}',
        body='Please find attached your invoice.',
        from_email='your_email@gmail.com',
        to=[invoice.client.email],  # Make sure Client model has email
    )
    email.attach(f'invoice_{invoice.id}.pdf', pdf_file.read(), 'application/pdf')
    email.send()

    return redirect('invoice_list')