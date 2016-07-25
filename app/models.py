# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from datetime import datetime
from django.conf import settings
import os

# Create your models here.

class MemberManager(BaseUserManager):
    """メンバー情報マネージクラス"""
    def create_user(self, number, name, full_name, email, birthday, gender, administrator, password=None):
        """
        Creates and saves a User
        """
        if not name:
            raise ValueError('名前は必須項目です')

        user = self.model(
            number=number,
            name=name,
            full_name=full_name,
            email=self.normalize_email(email),
            birthday=birthday,
            gender=gender,
            administrator=administrator,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password):
        """
        Creates and saves a superuser
        """
        user = self.create_user(
            number=0,
            name=name,
            full_name=name,
            email=name+'@sample.com',
            birthday=datetime.now(),
            gender=0,
            administrator=True,
            password=password,
        )
        user.save(using=self._db)
        return user


class Member(AbstractBaseUser):
    """メンバー情報モデルクラス"""
    number = models.IntegerField()
    name = models.CharField(max_length=200,unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255,unique=True)
    birthday = models.DateField()
    gender = models.IntegerField(default=0)
    administrator = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = 'name'

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.name

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are administrator
        return self.administrator

class Article(models.Model):
    """ニュース記事モデルクラス"""
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=10240)
    released_at = models.DateTimeField()
    expired_at = models.DateTimeField(null=True)
    member_only = models.BooleanField(default=False)

    __no_expiration = False

    def __str__(self):
        return self.title

    def IsNoExpiration(self):
        return self.__no_expiration;

class Entry(models.Model):
    """ブログ記事モデルクラス"""
    member = models.ForeignKey(Member, related_name="entry_member")
    votes = models.ManyToManyField(Member, through='Vote',through_fields=('entry', 'member'),)

    def __str__(self):              # __unicode__ on Python 2
        return self.title

    title = models.CharField(max_length=200)
    body = models.TextField(max_length=10240)
    posted_at = models.DateTimeField('date published')
    status = models.CharField(max_length=200,default='draft')

class Vote(models.Model):
    """投票（いいね）モデルクラス"""
    entry = models.ForeignKey(Entry)
    member = models.ForeignKey(Member)
    timestamp = models.DateTimeField('date published')

    def __str__(self):              # __unicode__ on Python 2
        return str(self.member) + ',' + str(self.entry) + '[entry_pk=' + str(self.entry.pk) + ']'


def delete_previous_file(function):
    """不要となる古いファイルを削除する為のデコレータ実装.
    :param function: メイン関数
    :return: wrapper
    """
    def wrapper(*args, **kwargs):
        """Wrapper 関数.
        :param args: 任意の引数
        :param kwargs: 任意のキーワード引数
        :return: メイン関数実行結果
        """
        self = args[0]

        # 保存前のファイル名を取得
        result = MemberImage.objects.filter(pk=self.pk)
        previous = result[0] if len(result) else None

        # 関数実行
        result = function(*args, **kwargs)

        # 関数によってオブジェクトが削除された場合は強制的にファイルも削除する
        images = MemberImage.objects.filter(pk=self.pk)
        allways = len(images)==0
        # 保存前のファイルがあったら削除
        if previous and previous.image and (not self.image or allways or previous.image.url != self.image.url):
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, previous.image.name))
            except:
                pass        #ファイルが存在しない場合は無視する
        return result
    return wrapper

class MemberImage(models.Model):
    """メンバー画像モデルクラス"""
    member = models.OneToOneField(Member)
    image = models.ImageField(upload_to='images/%Y/%m/%d', blank=True, null=True)

    @delete_previous_file
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(MemberImage, self).save()

    @delete_previous_file
    def delete(self, using=None, keep_parents=False):
        super(MemberImage, self).delete()

    def __str__(self):              # __unicode__ on Python 2
        return '[member=' + str(self.member)  + '] [url=' + str(self.image.url) + ']'
