from django import forms 
from .models import Task

class CreateTaskForm(forms.ModelForm): #ModelForm me permite extender y personalizar mi formulario en base a un modelo asociado
    class Meta:
        model = Task  #Especifico el modelo al cual estará asociado el formulario
        fields = ['title', 'description', 'important']  #y los campos de ese modelo que quiero incluir
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Write a description'}),
            'important': forms.CheckboxInput(attrs={'class':'form-check-input md-auto'}),
        }

