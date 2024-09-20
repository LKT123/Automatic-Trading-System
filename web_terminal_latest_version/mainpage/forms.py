from django import forms

class StockForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',
                                                               'class': 'rounded-pill btn btn-lg btn-outline-primary',
                                                               'style': 'width: 150px;'
                                                               }))
    end_date  = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',
                                                               'class': 'rounded-pill btn btn-lg btn-outline-primary',
                                                               'style': 'width: 150px;'
                                                               }))
    stock_code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'rounded-pill btn btn-lg btn-outline-primary',
                                                                              'style': 'width: 120px;'
                                                                              }))
    CHOICES = [
        ('Enable Fed Decision', 'Enable Fed Decision'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Model A', 'Model A'),
        ('Core Inflation Rate YoY', 'Core Inflation Rate YoY'),
        ('PPI YoY', 'PPI YoY'),
        ('Non Farm Payrolls', 'Non Farm Payrolls'),
        ('Initial Jobless Claims', 'Initial Jobless Claims'),
        ('Retail Sales MoM', 'Retail Sales MoM'),
        ('Durable Goods Orders MoM', 'Durable Goods Orders MoM'),
        ('Core PCE Price Index MoM', 'Core PCE Price Index MoM'),
        ('ISM Manufacturing PMI', 'ISM Manufacturing PMI'),
        ('ADP Employment Change', 'ADP Employment Change'),
        ('Unemployment Rate', 'Unemployment Rate'),
        ('ISM Services PMI', 'ISM Services PMI'),
        ('Negative Core Inflation Rate YoY', '--negative impact'),
        ('Negative PPI YoY', '--negative impact'),
        ('Negative Non Farm Payrolls', '--negative impact'),
        ('Negative Initial Jobless Claims', '--negative impact'),
        ('Negative Retail Sales MoM', '--negative impact'),
        ('Negative Durable Goods Orders MoM', '--negative impact'),
        ('Negative Core PCE Price Index MoM', '--negative impact'),
        ('Negative ISM Manufacturing PMI', '--negative impact'),
        ('Negative ADP Employment Change', '--negative impact'),
        ('Negative Unemployment Rate', '--negative impact'),
        ('Negative ISM Services PMI', '--negative impact'),
    ]
    economic_indicators = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}),
        required=False,
        label='Select your options')