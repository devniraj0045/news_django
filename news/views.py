from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Article, Category, Tag
from .forms import CommentForm


def home(request):
    # 1. Featured News (High priority)
    featured_news = Article.objects.filter(status='published', is_featured=True).order_by('-published_at')[:5]
    
    # 2. Latest News (Chronological) - Exclude featured to avoid duplicates if needed, or just show all
    latest_news = Article.objects.filter(status='published').order_by('-published_at')[:8]
    
    # 3. Trending / Popular (Based on views)
    trending_news = Article.objects.filter(status='published').order_by('-views')[:5]
    
    # 4. Category Blocks (3-4 recent articles per category)
    # Fetch major categories, or all. 
    categories = Category.objects.all()
    category_sections = []
    for cat in categories:
        articles = cat.articles.filter(status='published').order_by('-published_at')[:4]
        if articles:
            category_sections.append({
                'category': cat,
                'articles': articles
            })
            
    context = {
        'featured_news': featured_news,
        'latest_news': latest_news,
        'trending_news': trending_news,
        'category_sections': category_sections,
        'categories': categories, # For nav
    }
    return render(request, 'news/home.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    article_list = category.articles.filter(status='published').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(article_list, 10) # 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'articles': page_obj, # Use page_obj instead of raw queryset
        'categories': Category.objects.all(),
    }
    return render(request, 'news/category_detail.html', context)

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    article_list = tag.articles.filter(status='published').order_by('-published_at')
    
    paginator = Paginator(article_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'articles': page_obj,
        'categories': Category.objects.all(),
    }
    return render(request, 'news/tag_detail.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    # Increment view count
    article.views += 1
    article.save()
    
    # Handle Comment Submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            return redirect('article_detail', slug=slug)
    else:
        form = CommentForm()

    # Get approved comments
    comments = article.comments.filter(is_approved=True).order_by('-created_at')

    # Related Articles
    related_articles = Article.objects.filter(
        Q(category=article.category) | Q(tags__in=article.tags.all())
    ).filter(status='published').exclude(id=article.id).distinct().order_by('-published_at')[:5]
    
    context = {
        'article': article,
        'comments': comments,
        'form': form,
        'related_articles': related_articles,
        'categories': Category.objects.all(),
    }
    return render(request, 'news/article_detail.html', context)

# ==========================================
# DASHBOARD VIEWS
# ==========================================
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ArticleForm, CategoryForm, SiteConfigForm
from .models_config import SiteConfiguration

@staff_member_required
def dashboard_home(request):
    total_articles = Article.objects.count()
    total_views = sum([a.views for a in Article.objects.all()])
    recent_articles = Article.objects.order_by('-created_at')[:5]
    
    context = {
        'total_articles': total_articles,
        'total_views': total_views,
        'recent_articles': recent_articles,
    }
    return render(request, 'news/dashboard/home.html', context)

# --- Article CRUD ---
@staff_member_required
def dashboard_article_list(request):
    articles = Article.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'news/dashboard/article_list.html', {'articles': articles})

@staff_member_required
def dashboard_article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m() # Save tags
            return redirect('dashboard_article_list')
    else:
        form = ArticleForm()
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Create Article'})

@staff_member_required
def dashboard_article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk, is_deleted=False)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('dashboard_article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Edit Article'})

@staff_member_required
def dashboard_article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.is_deleted = True # Soft Delete
        article.save()
        return redirect('dashboard_article_list')
    return render(request, 'news/dashboard/confirm_delete.html', {'object': article})

# TRASH / BACKUP VIEWS
@staff_member_required
def dashboard_trash(request):
    deleted_articles = Article.objects.filter(is_deleted=True).order_by('-updated_at')
    return render(request, 'news/dashboard/trash.html', {'articles': deleted_articles})

@staff_member_required
def dashboard_restore_article(request, pk):
    article = get_object_or_404(Article, pk=pk, is_deleted=True)
    article.is_deleted = False
    article.save()
    return redirect('dashboard_trash')

@staff_member_required
def dashboard_force_delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk, is_deleted=True)
    if request.method == 'POST':
        article.delete() # Permanent Delete
        return redirect('dashboard_trash')
    return render(request, 'news/dashboard/confirm_delete.html', {'object': article, 'permanent': True})

# --- Category CRUD ---
@staff_member_required
def dashboard_category_list(request):
    categories = Category.objects.all()
    return render(request, 'news/dashboard/category_list.html', {'categories': categories})

@staff_member_required
def dashboard_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_category_list')
    else:
        form = CategoryForm()
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Create Category'})

@staff_member_required
def dashboard_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('dashboard_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Edit Category'})

@staff_member_required
def dashboard_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('dashboard_category_list')
    return render(request, 'news/dashboard/confirm_delete.html', {'object': category})

# --- Settings ---
@staff_member_required
def dashboard_settings(request):
    config, _ = SiteConfiguration.objects.get_or_create()
    if request.method == 'POST':
        form = SiteConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('dashboard_home')
    else:
        form = SiteConfigForm(instance=config)
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Site Settings'})

@staff_member_required
def dashboard_breaking_news(request):
    config, _ = SiteConfiguration.objects.get_or_create()
    from .forms import BreakingNewsForm 
    if request.method == 'POST':
        form = BreakingNewsForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('dashboard_home')
    else:
        form = BreakingNewsForm(instance=config)
    return render(request, 'news/dashboard/form.html', {'form': form, 'title': 'Manage Breaking News'})

@staff_member_required
def dashboard_activity_log(request):
    from .models_activity import ActivityLog
    
    user_id = request.GET.get('user_id')
    if user_id:
        logs = ActivityLog.objects.filter(user_id=user_id).order_by('-timestamp')
    else:
        logs = ActivityLog.objects.all().order_by('-timestamp')
        
    return render(request, 'news/dashboard/activity_log.html', {'logs': logs})
