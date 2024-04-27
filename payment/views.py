from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, redirect
from .models import Payment
from .forms import PaymentForm

def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'burger/payment.html', {'payments': payments})

def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment_list')
    else:
        form = PaymentForm()
    return render(request, 'burger/add_payment.html', {'form': form})
