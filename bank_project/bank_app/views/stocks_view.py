from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..errors import InsufficientFunds
from ..forms import StockForm
from bank_app.models import Customer, Stock


@login_required
def stocks(request):
    print("In the stocks view")
    assert hasattr(
        request.user, 'customer'), 'Staff user routing customer view.'
    # get stocks from bank/available stocks to buy
    # get stocks from customer
    # customer = Customer.objects.get(user=request.user)
    bank = Customer.default_bank_acc().customer
    available_stocks_to_buy = bank.stocks
    # print("Available stocks to buy: ", available_stocks_to_buy)
    customer = request.user.customer
    customer_stocks = customer.stocks
    # print("Customer socks: ", customer_stocks)
    context = {'available_stocks_to_buy': available_stocks_to_buy,
               'customer_stocks': customer_stocks}
    return render(request, 'bank_app/stocks.html', context)


@login_required
def buy_stocks(request, stock_symbol=None):
    print("In the buy_stocks view")
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    # bank = Customer.default_bank_acc().customer
    # available_stock_to_buy = Stock.stock(bank, stock_symbol)
    # context = {'available_stock_to_buy': available_stock_to_buy}
    # if request.method == 'POST':
    # return render(request, 'bank_app/buy_stock.html', context)

    bank_account = Customer.default_bank_acc()
    bank = bank_account.customer

    available_stocks_to_buy = bank.stocks
    if request.method == 'POST':
        form = StockForm(request.POST)
        form.fields['stock'].queryset = available_stocks_to_buy
        form.fields['customer_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            stock_of_seller = form.cleaned_data['stock']
            stock_volume = form.cleaned_data['stock_volume']
            stock_buyer_account = form.cleaned_data['customer_account']
            stock_seller_account = bank_account  # we buy stocks from the bank
            stock_of_buyer = Stock.stock(
                stock_buyer_account.customer, stock_of_seller.stock_symbol) or None
            print("buy_stocks > stock_of_seller",
                  stock_of_seller, type(stock_of_seller))
            print("buy_stocks > stock_volume",
                  stock_volume, type(stock_volume))
            print("buy_stocks > stock_buyer_account",
                  stock_buyer_account, type(stock_buyer_account))
            print("buy_stocks > stock_seller_account",
                  stock_seller_account, type(stock_seller_account))
            print("buy_stocks > stock_of_buyer",
                  stock_of_buyer, type(stock_of_buyer))
            try:
                Stock.transfer_stock(
                    stock_volume, stock_of_seller, stock_seller_account, stock_buyer_account, stock_of_buyer)
                # Recurring_Payment.pay_recurring_payments_for_today()
                return stocks(request)
            except InsufficientFunds:
                form._errors['customer_account'] = form.error_class([f'Not enough funds to perform the purchase'])
                # context = {
                #     'title': 'Payment error',
                #     'error': 'Insufficient funds to set a recurring payment'
                # }
                # return render(request, 'bank_app/error.html', context)

    else:
        form = StockForm()
    print("request.user.customer.accounts: ", request.user.customer.accounts)
    form.fields['stock'].queryset = available_stocks_to_buy
    form.fields['customer_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/buy_stocks.html', context)


@login_required
def sell_stocks(request, stock_symbol=None):
    print("In the sell_stocks view")
    assert hasattr(request.user, 'customer'), 'Staff user routing customer view.'
    # bank = Customer.default_bank_acc().customer
    # available_stock_to_buy = Stock.stock(bank, stock_symbol)
    # context = {'available_stock_to_buy': available_stock_to_buy}
    # if request.method == 'POST':
    # return render(request, 'bank_app/buy_stock.html', context)

    bank_account = Customer.default_bank_acc()
    bank = bank_account.customer
    if request.method == 'POST':
        form = StockForm(request.POST)
        form.fields['stock'].queryset = request.user.customer.stocks
        form.fields['customer_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            stock_of_seller = form.cleaned_data['stock']
            stock_volume = form.cleaned_data['stock_volume']
            stock_seller_account = form.cleaned_data['customer_account']
            stock_buyer_account = bank_account  # we sell stocks to the bank
            stock_of_buyer = Stock.stock(
                bank, stock_of_seller.stock_symbol) or None
            try:
                Stock.transfer_stock(
                    stock_volume, stock_of_seller, stock_seller_account, 
                    stock_buyer_account, stock_of_buyer)
                # Recurring_Payment.pay_recurring_payments_for_today()
                return stocks(request)
            except InsufficientFunds:
                context = {
                    'title': 'Payment error',
                    'error': 'Insufficient funds to set a recurring payment'
                }
                return render(request, 'bank_app/error.html', context)

    else:
        form = StockForm()
    form.fields['stock'].queryset = request.user.customer.stocks
    form.fields['customer_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank_app/sell_stocks.html', context)