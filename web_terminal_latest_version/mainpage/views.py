from dbm import error
from django.shortcuts import render
from .forms import StockForm
# Create your views here.
from django.http import HttpResponse
from .apps import terminal_manager




def home(request):
    # 假设 home.html 在 mainpage/templates/mainpage/ 目录下
    data = {
        'labels': [1,2,3,4],
        'values': [10, 20, 30, 40]
    }
    # Get data from the terminal_manager
    try:
        result =  terminal_manager._cache['home.html timesfm']
    except error as e:
        print(e)
        result = [[],[]]
    
    
    return render(request, 'mainpage/home.html', {'price_List': result[0], 'prediction_List': result[1]})
    
    
    #return render(request, 'mainpage/home.html')

def about(request):
    # 假设 about.html 在 mainpage/templates/mainpage/ 目录下
    return render(request, 'mainpage/about.html')

def contact(request):
    # 假设 contact.html 在 mainpage/templates/mainpage/ 目录下
    return render(request, 'mainpage/contact.html')

def timesfmweb(request):
    return render(request, 'mainpage/timesfmweb.html')

def account(request):
    return render(request, 'mainpage/account.html')

def analysis(request):
    return render(request, 'mainpage/analysis.html')

def backwardtest(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            # 这里处理你的表单数据
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            stock_code = form.cleaned_data['stock_code']
            raw_settings = form.cleaned_data['economic_indicators']
                        
            """
            
            Call the trading terminal to do a simulation test
            
            """
            result = terminal_manager.backward_test(start_date, end_date, stock_code, raw_settings)            
            
            # Secure concerm
            if not result:
                return render(request, 'mainpage/backwardtest.html', {'stock_code': "<Invalid Input>", 'backwardtest_stockform': StockForm()})             
            
            # Update views
            return render(request, 'mainpage/backwardtest.html', {
                'stock_code': stock_code,
                'backwardtest_stockform': form,
                'account_result': result[0],
                'baseline_result': result[1],
                'profit': result[2],
                'max_loss': result[3],
                'decision_array': result[4]
                })
        else:
            print(form.errors)
    else:
        form = StockForm()
    
    return render(request, 'mainpage/backwardtest.html', {'stock_code': "----", 'backwardtest_stockform': form, "have_indicator": "No"})
    
def setting(request):
    return render(request, 'mainpage/setting.html')





