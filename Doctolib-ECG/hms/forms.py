from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, 
                             widget=forms.EmailInput(
                                 attrs={
                                     'class': 'custom-input',
                                     'id': 'email',
                                     'placeholder': 'Enter Email Address'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'custom-input',
            'id': 'password', 'placeholder': 'Enter Password'}
        ))
    

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Sélectionner un fichier CSV',
        help_text='Le fichier doit être au format CSV',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.csv'
        })
    )

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('Le fichier doit être au format CSV')
        if file.size > 5242880:  # 5MB limit
            raise forms.ValidationError('La taille du fichier doit être en dessous de 5MB')
        return file
