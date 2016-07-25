# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from .models import Member, Article, Entry, MemberImage
from datetime import datetime
from django.utils import timezone


class SearchForm(forms.Form):
    search_name = forms.CharField(
        label='名前',
        max_length = 20,
        required=True,
        widget=forms.TextInput()
    )

class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ['number', 'name', 'full_name', 'gender', 'birthday', 'email', 'administrator']
        labels = {
            'number': ('背番号'),
            'name': ('ユーザー名'),
            'full_name': ('氏名'),
#            'gender': ('性別'),
#            'birthday': ('誕生日'),
            'email': ('メールアドレス'),
#            'administrator': ('管理者'),
        }
        localized_fields = ('birthday',)

    CHOICES=[(0,'男'),(1,'女')]

#    number = forms.IntegerField(label='背番号')
#    name   = forms.CharField(label='ユーザー名')
#    full_name = forms.CharField(label='氏名')
    gender = forms.ChoiceField(label='性別', choices=CHOICES, widget=forms.RadioSelect(), initial=0 )
    birthday = forms.DateField(label='誕生日',input_formats=('%Y/%m/%d','%Y-%m-%d',))
#    email = forms.EmailField(label='メールアドレス')
    administrator = forms.BooleanField(label='管理者',required=False)

class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'body', 'released_at', 'no_expired_at', 'expired_at', 'member_only']
        labels = {
            'title': ('タイトル'),
            'body': ('本文'),
        }
        localized_fields = ('released_at', 'expired_at', )

    INPUT_FORMATS=('%Y/%m/%d %H:%M','%Y-%m-%d %H:%M','%Y/%m/%d %H:%M:%S','%Y-%m-%d %H:%M:%S')
    released_at = forms.DateTimeField(label='掲載開始日時',input_formats=INPUT_FORMATS)
    expired_at  = forms.DateTimeField(label='掲載終了日時',input_formats=INPUT_FORMATS)
    member_only = forms.BooleanField(label='会員限定',required=False)
    no_expired_at = forms.BooleanField(label='掲載終了日時を設定しない',required=False)

    def clean(self):
        cleaned_data = super(ArticleForm, self).clean()
        released_at = cleaned_data.get("released_at")
        expired_at  = cleaned_data.get("expired_at")
        no_expired_at  = cleaned_data.get("no_expired_at")
        if released_at != None and expired_at != None and released_at > expired_at and no_expired_at == False:
            self.add_error('expired_at', '掲載終了日時は掲載開始日時より後にしてください。')
        else:
            if no_expired_at == True and 'expired_at' in self._errors:
                del self._errors['expired_at']
                if 'expired_at' not in cleaned_data:
                    cleaned_data['expired_at'] = datetime.now()
        return cleaned_data

class AccountForm(MemberForm):

    class Meta:
        model = Member
        fields = ['number', 'name', 'full_name', 'gender', 'birthday', 'email', 'password1', 'password2']
        labels = {
            'number': ('背番号'),
            'name': ('ユーザー名'),
            'full_name': ('氏名'),
            'email': ('メールアドレス'),
        }
        localized_fields = ('birthday',)

    administrator = None
    password = None
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput,required=False)
    password2 = forms.CharField(label='パスワードの確認', widget=forms.PasswordInput,required=False)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません。")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AccountForm, self).save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ['title', 'body', 'posted_at', 'status']
        labels = {
            'title': ('タイトル'),
            'body': ('本文'),
        }
        localized_fields = ('posted_at', )

    STATUS_CHOICES=[('draft','下書き'),('member_only','会員限定'),('public','公開')]
    INPUT_FORMATS=('%Y/%m/%d %H:%M','%Y-%m-%d %H:%M','%Y/%m/%d %H:%M:%S','%Y-%m-%d %H:%M:%S')

    posted_at = forms.DateTimeField(label='日時',input_formats=INPUT_FORMATS)
    status = forms.ChoiceField(required=False,label='状態',widget=forms.Select(), choices=STATUS_CHOICES)

    def clean(self):
        cleaned_data = super(EntryForm, self).clean()
        return cleaned_data

class MemberImageForm(forms.ModelForm):

    class Meta:
        model = MemberImage
        fields = {'image', 'delete_image' }
        labels = {
            'image': ('画像'),
        }

    delete_image = forms.BooleanField(label='削除する',required=False, initial=False)

    def clean(self):
        cleaned_data = super(MemberImageForm, self).clean()
        delete_image = cleaned_data.get("delete_image")
        if delete_image == True:
            cleaned_data['image'] = None
        return cleaned_data
