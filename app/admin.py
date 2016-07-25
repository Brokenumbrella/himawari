# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Register your models here.

from .models import Member, Article, Entry, MemberImage, Vote

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('number', 'name', 'full_name', 'email', 'gender', 'birthday', 'administrator')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
#    password = ReadOnlyPasswordHashField()
    password = None
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput,required=False)
    password2 = forms.CharField(label='パスワードの確認', widget=forms.PasswordInput,required=False)

    class Meta:
        model = Member
        fields = ('number', 'name', 'full_name', 'email', 'gender', 'birthday', 'administrator', 'password1', 'password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません。")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserChangeForm, self).save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

#    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
#        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('number', 'name', 'full_name', 'email', 'birthday', 'gender', 'administrator')
    list_filter = ('administrator',)
    fieldsets = (
        (None, {'fields': ('name', 'password1', 'password2')}),
        ('Personal info', {'fields': ('number',)}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Personal info', {'fields': ('email',)}),
        ('Personal info', {'fields': ('birthday',)}),
        ('Personal info', {'fields': ('gender',)}),
        ('Permissions', {'fields': ('administrator',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('number', 'name', 'full_name', 'gender', 'birthday', 'email', 'administrator', 'password1', 'password2')}
        ),
    )
    search_fields = ('name',)
    ordering = ('number',)
    filter_horizontal = ()

admin.site.register(Member, UserAdmin)
admin.site.register(Article)
admin.site.register(Entry)
admin.site.register(MemberImage)
admin.site.register(Vote)

admin.site.unregister(Group)
