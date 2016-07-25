# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from datetime import timedelta

from .models import Member, Article, Entry, MemberImage, Vote
#import locale
#from app.views import locale
from django import forms
from django.db.models import Q

from app.forms import MemberForm, ArticleForm, AccountForm, EntryForm, MemberImageForm, SearchForm
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponseForbidden

from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import DeleteView
from _datetime import timedelta
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
import functools

import locale
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import update_session_auth_hash

if settings.DEBUG:
    MEMBER_LIST_PAGE_IN_COUNT = 5
    ARTICLER_LIST_PAGE_IN_COUNT = 5
    ENTRY_LIST_PAGE_IN_COUNT = 5
else:
    MEMBER_LIST_PAGE_IN_COUNT = 15
    ARTICLER_LIST_PAGE_IN_COUNT = 5
    ENTRY_LIST_PAGE_IN_COUNT = 5


# Django標準のページネーション機能によるページ情報の取得
# objects_ : オブジェクトリスト
# page_no : 取得するページ数
# count   : ページに表示するオブジェクトの数
# 戻り値 : page　オブジェクト
def _get_page(objects_, page_no, count=1):
    
    paginator = Paginator(objects_, count)
    try:
        page = paginator.page(page_no)
    except (EmptyPage, PageNotAnInteger):
        page = paginator.page(1)
    return page

# ログイン状態確認用デコレータ
def login_required(is_staff_=False):
    def preprocess(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # View の Request オブジェクトを取り出す
            request = args[0]

            # ログイン状態を取得
            #if not request.session.get('logged_in'):
            if not(request.user and request.user.is_authenticated() and ( not is_staff_ or request.user.is_staff) ):
            #is_staff__ = is_staff_ == False or request.user.is_staff
            #if not(request.user and request.user.is_authenticated() and is_staff__ ):
                #raise Http404
                return HttpResponseForbidden()

            return func(*args, **kwargs)
        return wrapper
    return preprocess

@login_required()
def user_profile(request):
    context = RequestContext(request,
                             {'user': request.user})
    return render_to_response('accounts/user_profile.html',
                              context_instance=context)

def login_after(request):
    return HttpResponseRedirect(reverse('home'))

"""
日付データを文字列に変換(Unicode文字列が含まれていると UnicodeEncodeError が出るのでそれを回避）
  format : u'%Y年%m月%d日' のようにフォーマット文字列を指定します
  dt : datetime オブジェクトを指定します
"""
def datetime_to_str(format,dt):
    strdatetime = dt.strftime(format.encode('unicode-escape').decode()).encode().decode('unicode-escape')
    return strdatetime

def get_article_list( order_by, member ):
    """
    ニュース一覧を取得
        order_by : ソートオーダーを指定します。例）'-released_at':公開日付の新しい順
        member   : メンバーの場合は True を、ゲストの場合は False を指定します。（Falseの場合はメンバーオンリーのニュースは除外されます）
    """
    now = datetime.now()
    q = Q(released_at__lte=now) & (Q(expired_at=None) | Q(expired_at__gte=now))     #公開日以降で公開終了日が未設定か終了日前なら表示する。
    if not member:
        q &= Q(member_only=False)                                                   #ゲストはメンバーオンリーのニュースを表示しない
    article_list = Article.objects.filter(q).order_by(order_by)
    return article_list

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    #article_list = Article.objects.order_by('-released_at')[:5]
    login = request.user and request.user.is_authenticated()
    article_list = get_article_list('-released_at',login)[:5]
    auth_form = AuthenticationForm(None, request.POST or None)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'articles':article_list if len(article_list) else None,
            'blogs':EntryView.get_entry_list('-posted_at',-1, -1 if not login else request.user.pk )[:5],
            'auth_form':auth_form,
            'current_user':request.user,
            'current_page':request.path,  #'home'
#            'datestr':datetime_to_str('%Y鷗外%m月%d日', datetime.now()), #datetime.now().strftime('%Y鷗外%m月%d日'),
#            'currentlocale':locale.getlocale(locale.LC_TIME)
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    login = request.user and request.user.is_authenticated()
    article_list = get_article_list('-released_at',login)[:5]
    auth_form = AuthenticationForm(None, request.POST or None)
    return render(
        request,
        'app/about.html',
        {
            'title':'このサイトについて',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, -1 if not login else request.user.pk )[:5],
            'auth_form':auth_form,
            'current_user':request.user,
        }
    )

###############
# 会員情報
###############
class MemberView(TemplateView):
    @login_required()
    def list(request):
        """Renders the member list page."""
        assert isinstance(request, HttpRequest)

        form = SearchForm(request.GET or None)
        if form.is_valid():
            search_name = form.data['search_name']
            member_list = Member.objects.filter( Q(name__icontains=search_name) | Q(full_name__icontains=search_name) ).order_by('number')
        else:
            member_list = Member.objects.filter( number__gte=1 ).order_by('number')

        page_no = request.GET.get('page')
        page = _get_page(member_list, page_no, MEMBER_LIST_PAGE_IN_COUNT )
        article_list = Article.objects.order_by('-released_at')[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(
            request,
            'app/member_list.html',
            {
                'title':'会員名簿',
                'year':datetime.now().year,
                'articles':article_list,
                'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
                'contents':range(1,6),
                'member_list':page.object_list,
                'form':form,
                'auth_form':auth_form,
                'current_user':request.user,
                'page' : page,
                'current_page':request.path  #'member_list'
            }
        )
    """
    メンバーの詳細ページ
    メンバー、アカウント両方から呼べるように別メソッドを用意
    """
    def _detail(request, member_id, account_mode):
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            raise Http404("Member does not exist")
        try:
            memberimage = MemberImage.objects.get(member__pk=member_id)
        except MemberImage.DoesNotExist:
            memberimage = None
        article_list = Article.objects.order_by('-released_at')[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(request, 'app/member_detail.html', { 
                'title': '会員の詳細' if not account_mode else 'マイアカウント',
                'year':datetime.now().year,
                'articles':article_list,
                'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
                'member': member,
                'auth_form':auth_form,
                'current_user':request.user,
                'memberimage':memberimage,
                'account_mode': account_mode,
            }
        )
    
    @login_required()
    def detail(request, member_id):
        return MemberView._detail(request, member_id,False)
        
    @login_required(True)
    def new(request):
        """ 新規メンバー追加ページ """
        if request.method == 'POST': # フォームが提出された
            form = MemberForm(request.POST) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                member = form.save(commit=False)
                member.save()
                return HttpResponseRedirect(reverse('member_list')) # POST 後のリダイレクト
        else:
            form = MemberForm() # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        return render(request, 'app/member_edit.html', { 
            'form': form,
            'title':'会員の新規登録',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'登録',
            'current_user':request.user,
        })
    
    def _edit(request, member_id,account_mode):
        """ メンバー編集ページの下請け"""
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            raise Http404("Member does not exist")
        try:
            memberimage = MemberImage.objects.get(member__pk=member_id)
        except MemberImage.DoesNotExist:
            memberimage = MemberImage()
            memberimage.member = member
        if request.method == 'POST': # フォームが提出された
            form = MemberForm(request.POST, instance = member) if not account_mode else AccountForm(request.POST, instance = member) # POST データの束縛フォーム
            imgform = MemberImageForm(request.POST, request.FILES, instance = memberimage) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                if imgform.is_valid():
                    form.save()
                    if account_mode and form.cleaned_data['password1']:
                        update_session_auth_hash(request, form.instance)
                    memberimage = imgform.save(commit=False)
                    if imgform.cleaned_data['delete_image'] == True:
                        memberimage.delete()
                    elif memberimage.image:
                        memberimage.save()
                    redirect_url = reverse('account_detail',kwargs={'member_id':member_id}) if account_mode else reverse('member_detail',kwargs={'member_id':member_id})
                    return HttpResponseRedirect( redirect_url ) # POST 後のリダイレクト
        else:
            form = MemberForm(instance = member) if not account_mode else AccountForm(instance = member) # 非束縛フォーム
            imgform = MemberImageForm(instance = memberimage) # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        return render(request, 'app/member_edit.html', { 
            'form': form,
            'title':'会員の編集' if not account_mode else 'アカウント情報の編集',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'更新',
            'member_pk':member.pk,
            'current_user':request.user,
            'imgform':imgform,
            'account_mode': account_mode,
        })

    @login_required(True)
    def edit(request, member_id):
        """ メンバー編集ページ"""
        return MemberView._edit(request, member_id,False)

    @login_required(True)
    def delete(request, member_id):
        """ メンバー削除処理"""
        try:
            memberimage = MemberImage.objects.get(member__pk=member_id)
            memberimage.delete()
        except:
            pass
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            raise Http404("メンバーが存在しません")
        member.delete()
        return HttpResponseRedirect(reverse('member_list'))

###############
# アカウント
###############
# /accounts/1/profile/
class AccountView(TemplateView):
    @login_required()
    def detail(request,member_id):
        """ マイアカウントページ"""
        return MemberView._detail(request,member_id,True)

    @login_required()
    def edit(request,member_id):
        """ マイアカウントの編集ページ"""
        return MemberView._edit(request,member_id,True)

###############
# ニュース
###############
class ArticleView(TemplateView):
    def list(request):
        """Renders the article list page."""
        assert isinstance(request, HttpRequest)
        login = request.user and request.user.is_authenticated()
        article_list = get_article_list('-released_at',login)
        page_no = request.GET.get('page')
        page = _get_page(article_list, page_no, ARTICLER_LIST_PAGE_IN_COUNT )
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(
            request,
            'app/article_list.html',
            {
                'title':'ニュース一覧',
                'year':datetime.now().year,
                'articles':article_list[:5],
                'blogs':EntryView.get_entry_list('-posted_at',-1, -1 if not login else request.user.pk )[:5],
                'contents':range(1,6),
                'article_list':page.object_list,
                'auth_form':auth_form,
                'current_user':request.user,
                'page' : page,
                'current_page':request.path  #'article_list'
            }
        )
    
    def detail(request, article_id):
        """Renders the article detail page."""
        try:
            article = Article.objects.get(pk=article_id)
        except Member.DoesNotExist:
            raise Http404("Article does not exist")
        #article_list = Article.objects.order_by('-released_at')[:5]
        login = request.user and request.user.is_authenticated()
        article_list = get_article_list('-released_at',login)[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(request, 'app/article_detail.html', { 
                'title':'ニュースの詳細',
                'year':datetime.now().year,
                'articles':article_list,
                'blogs':EntryView.get_entry_list('-posted_at',-1, -1 if not login else request.user.pk )[:5],
                'article': article,
                'auth_form':auth_form,
                'current_user':request.user,
            }
        )
    
    @login_required()
    def new(request):
        """Renders the new article page."""
        if request.method == 'POST': # フォームが提出された
            form = ArticleForm(request.POST) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                article = form.save(commit=False)
                if form.cleaned_data['no_expired_at'] is True:
                    article.expired_at = None
                article.save()
                return HttpResponseRedirect(reverse('article_list')) # POST 後のリダイレクト
        else:
            form = ArticleForm() # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(request, 'app/article_edit.html', { 
            'form': form,
            'title':'ニュース記事の新規登録',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'登録する',
            'auth_form':auth_form,
            'current_user':request.user,
        })

    @login_required()
    def edit(request, article_id):
        """Renders the article edit page."""
        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            raise Http404("Article does not exist")
        if request.method == 'POST': # フォームが提出された
            form = ArticleForm(request.POST, instance = article) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                article = form.save(commit=False)
                if form.cleaned_data['no_expired_at'] is True:
                    article.expired_at = None
                article.save()
                return HttpResponseRedirect(reverse('article_list')) # POST 後のリダイレクト
        else:
            no_expired_at = False
            if article.expired_at is None:
                no_expired_at = True
                article.expired_at = datetime.now() + timedelta(days=1)
            form = ArticleForm(instance = article, initial = {'no_expired_at': no_expired_at, }) # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(request, 'app/article_edit.html', { 
            'form': form,
            'title':'ニュース記事の編集',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'更新する',
            'article_pk':article.pk,
            'auth_form':auth_form,
            'current_user':request.user,
        })

    @login_required()
    def delete(request, article_id):
        """article delete."""
        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            raise Http404("Article does not exist")
        article.delete()
        return HttpResponseRedirect(reverse('article_list'))

###############
# ブログ
###############
class EntryView(TemplateView):
    def get_entry_list( order_by, member_id=-1, login_user_id=-1 ):
        """get entry list."""
        q = Q(status='public')
        if member_id>=0 :
            q = Q(member__pk=member_id)
            if member_id != login_user_id:
                q &= ~Q(status='draft')
        elif login_user_id>=0:
            # ログインユーザーは下書きも出る、それ以外は下書きが出ない
            q = Q(member__pk=login_user_id) | ~Q(status='draft')
        entry_list = Entry.objects.filter(q).order_by(order_by)
        return entry_list

    def __index(request,member_id=-1):
        """Renders the entry list page."""
        assert isinstance(request, HttpRequest)
        try:
            member_id = int(member_id)  #数値化（数値に対しても問題なく使える）
        except :
            member_id = -1              #例外が出た場合はデフォルトの-1を入れておく
        if member_id!=-1:
            try:
                member = Member.objects.get(pk=member_id)
            except Member.DoesNotExist:
                raise Http404("Member does not exist")

        login = request.user and request.user.is_authenticated()
        login_user_id = -1 if not login else request.user.pk
        entry_list = EntryView.get_entry_list('-posted_at',member_id, login_user_id)
        page_no = request.GET.get('page')
        page = _get_page(entry_list, page_no, ENTRY_LIST_PAGE_IN_COUNT )
        auth_form = AuthenticationForm(None, request.POST or None)
        title = ('会員' if member_id==-1 else (member.name +'さん')) + 'のブログ'       #タイトル文字列の変更
        return render(
            request,
            'app/entry_list.html',
            {
                'title':title,   #'会員のブログ',
                'year':datetime.now().year,
                'articles':Article.objects.order_by('-released_at')[:5],
                'blogs':EntryView.get_entry_list('-posted_at',-1, login_user_id)[:5],
                'entry_list':page.object_list,
                'auth_form':auth_form,
                'current_user':request.user,
                'page' : page,
                'current_page':request.path  #'entry_list'
            }
        )

    def list(request):
        """Renders the entry list page."""
        return EntryView.__index(request)

    def entry_member(request,member_id):
        """Renders the member entry list page."""
        return EntryView.__index(request,member_id)

    def detail(request,entry_id):
        """Renders the entry detail page."""
        assert isinstance(request, HttpRequest)
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Member.DoesNotExist:
            raise Http404("指定されたブログが見つかりません")

        login = request.user and request.user.is_authenticated()
        if not login and entry.status != 'public':                      # ログインしてない場合は public 以外表示しない
            return HttpResponseForbidden()                              # アドレスをコピペしなければ通常は起こらないため例外処理で済ませておく。

        login_user_id = -1 if not login else request.user.pk
        entry_list = EntryView.get_entry_list('-posted_at',-1, login_user_id)
        auth_form = AuthenticationForm(None, request.POST or None)
        title = entry.member.name + 'さんのブログ'       #タイトル文字列の変更
        votes = Vote.objects.filter(entry__pk=entry.pk).order_by('-timestamp')
        show_vote_btn = True if login and login_user_id != entry.member.pk else False

        try:
            voteuser = votes.get(member__pk=login_user_id)
            show_vote_btn = show_vote_btn and (voteuser == None)
        except :
            pass

        return render(
            request,
            'app/entry_detail.html',
            {
                'title':title,   #'会員のブログ',
                'year':datetime.now().year,
                'articles':Article.objects.order_by('-released_at')[:5],
                'blogs':EntryView.get_entry_list('-posted_at',-1, login_user_id)[:5],
                'entry':entry,
                'auth_form':auth_form,
                'current_user':request.user,
                'votes':votes,   #order_by('-vote__timestamp'),
                'show_vote_btn': show_vote_btn,
            }
        )

    @login_required()
    def new(request):
        """Renders the new entry page."""
        assert isinstance(request, HttpRequest)
        if request.method == 'POST': # フォームが提出された
            form = EntryForm(request.POST) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                entry = form.save(commit=False)
                entry.member = request.user
                entry.save()
                return HttpResponseRedirect(reverse('entry_list')) # POST 後のリダイレクト
        else:
            form = EntryForm() # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        auth_form = AuthenticationForm(None, request.POST or None)
        return render(request, 'app/entry_edit.html', { 
            'form': form,
            'title':'ブログ記事の新規登録',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'登録する',
            'auth_form':auth_form,
            'current_user':request.user,
        })

    @login_required()
    def edit(request,entry_id):
        """Renders the entry edit page."""
        assert isinstance(request, HttpRequest)
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            raise Http404("指定されたブログが存在しません。")
        if not request.user or request.user.pk != entry.member.pk:      # ブログ作成者以外は編集できない
            return HttpResponseForbidden()                              #アドレスをコピペしなければ通常は起こらないため例外処理で済ませておく。

        if request.method == 'POST': # フォームが提出された
            form = EntryForm(request.POST, instance = entry) # POST データの束縛フォーム
            if form.is_valid(): # バリデーションを通った
                form.save()
                return HttpResponseRedirect(reverse('entry_list')) # POST 後のリダイレクト
        else:
            form = EntryForm(instance = entry) # 非束縛フォーム
        article_list = Article.objects.order_by('-released_at')[:5]
        return render(request, 'app/entry_edit.html', { 
            'form': form,
            'title':'ブログ記事の編集',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'submit_title':'更新',
            'entry_pk':entry.pk,
            'current_user':request.user,
        })

    @login_required()
    def delete(request,entry_id):
        """entry delete."""
        assert isinstance(request, HttpRequest)
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            raise Http404("指定されたブログが存在しません。")
        if not request.user or request.user.pk != entry.member.pk:      # ブログ作成者以外は編集できない
            return HttpResponseForbidden()                              #アドレスをコピペしなければ通常は起こらないため例外処理で済ませておく。
    
        # 本来ここらで確認メッセージを出したいところなんだが・・・どうやれば良いのだろう？

        entry.delete()
        return HttpResponseRedirect(reverse('entry_list'))

    @login_required()
    def like_entry(request,entry_id):
        """いいねが押された"""
        assert isinstance(request, HttpRequest)
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            raise Http404("指定されたブログが存在しません。")

        vote = Vote.objects.create(entry=entry, member=request.user,timestamp=datetime.now())
        vote.save()

        return HttpResponseRedirect( reverse('entry_detail', args=[entry_id]))

    @login_required()
    def voted_entry(request,member_id):
        """いいねの一覧"""
        assert isinstance(request, HttpRequest)
        try:
            votes = Vote.objects.filter(member__pk=member_id).order_by('-timestamp')
        except:
            votes = None

        article_list = Article.objects.order_by('-released_at')[:5]
        return render(request, 'app/voted_entry.html', { 
            'title':'投票した記事',
            'year':datetime.now().year,
            'articles':article_list,
            'blogs':EntryView.get_entry_list('-posted_at',-1, request.user.pk )[:5],
            'current_user':request.user,
            'votes':votes
        })

    @login_required()
    def unlike_entry(request,entry_id):
        """いいねの削除"""
        assert isinstance(request, HttpRequest)
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            raise Http404("指定されたブログが存在しません。")

        try:
            vote = Vote.objects.get(member__pk=request.user.pk, entry__pk=entry_id)
            vote.delete()
        except:
            pass

        return HttpResponseRedirect( reverse('voted_entry', args=[request.user.pk]))
