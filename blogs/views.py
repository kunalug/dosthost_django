# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Blog, Categories, Comment, Tag
from .forms import CommentForm
from django.core.paginator import Paginator
from django.http import JsonResponse

def blog_list(request):
    # Debug: Check if any blogs exist at all
    total_blogs = Blog.objects.count()
    print(f"Total blogs in database: {total_blogs}")
    
    # Fetch blogs with related data - try without select_related first
    blog_list = Blog.objects.all()
    paginator = Paginator(blog_list, 4)  # Show 4 blogs per page.

    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    
    # Debug: Print the actual blogs
    print(f"Blogs queryset: {blogs}")
    
    for blog in blogs:
        print(f"Blog: {blog.title}")
        print(f"Author: {blog.author}")
        print(f"Category: {blog.categories}")
        print("---")
    
    # Get recent posts
    recent_posts = Blog.objects.order_by('-created_at')[:4]
    
    # Get all categories
    all_categories = Categories.objects.all()
    tags = Tag.objects.all()
    
    # Check if blogs exist and add message if none
    if not blogs:
        messages.info(request, "No blogs have been posted yet.")
        print("No blogs found in database")
    else:
        print(f"Found {len(blogs)} blogs - they should display")

    context = {
        'blogs': blogs,
        'recent_posts': recent_posts,
        'all_categories': all_categories,
        'tags': tags,
        'page_title': "Blog",
        'total_blogs': total_blogs,  # Add this for debugging in template
    }
    
    print(f"Context blogs: {context['blogs']}")
    return render(request, 'pages/blog.html', context)

# Alternative view for debugging
def debug_blog_list(request):
    """Debug version to help identify the issue"""
    
    # Check database connection and models
    try:
        # Basic counts
        blog_count = Blog.objects.count()
        category_count = Categories.objects.count()
        
        print(f"Blog count: {blog_count}")
        print(f"Category count: {category_count}")
        
        # Get all blogs without any filtering
        all_blogs = Blog.objects.all()
        print(f"All blogs: {list(all_blogs.values('id', 'title', 'author__username', 'categories__name'))}")
        
        # Try different queries
        blogs_with_author = Blog.objects.filter(author__isnull=False)
        blogs_with_category = Blog.objects.filter(categories__isnull=False)
        
        print(f"Blogs with author: {blogs_with_author.count()}")
        print(f"Blogs with category: {blogs_with_category.count()}")
        
        context = {
            'blogs': all_blogs,
            'blog_count': blog_count,
            'category_count': category_count,
            'debug_info': {
                'total_blogs': blog_count,
                'blogs_with_author': blogs_with_author.count(),
                'blogs_with_category': blogs_with_category.count(),
            }
        }
        
        return render(request, 'pages/blog_debug.html', context)
        
    except Exception as e:
        print(f"Error in debug_blog_list: {e}")
        return render(request, 'pages/blog_debug.html', {'error': str(e)})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.filter(approved=True).order_by('-created_at')[:3]
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect('blogs:blog_detail', slug=blog.slug)

    recent_posts = Blog.objects.order_by('-created_at')[:4]
    all_categories = Categories.objects.all()
    tags = Tag.objects.all()
    context = {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
        'recent_posts': recent_posts,
        'all_categories': all_categories,
        'tags': tags,
    }
    return render(request, 'pages/blog-details.html', context)

def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': comment.likes.count()})

def blog_search(request):
    query = request.GET.get('q')
    if query:
        blogs = Blog.objects.filter(title__icontains=query)
    else:
        blogs = Blog.objects.all()

    paginator = Paginator(blogs, 4)  # Show 4 blogs per page.
    page_number = request.GET.get('page')
    blogs_page = paginator.get_page(page_number)

    context = {
        'blogs': blogs_page,
        'query': query,
        'page_title': "Blog",
    }
    return render(request, 'pages/blog.html', context)

def blog_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    blogs = Blog.objects.filter(tags=tag)
    context = {
        'blogs': blogs,
        'tag': tag,
        'page_title': f'Blogs tagged with "{tag.name}"'
    }
    return render(request, 'pages/blog.html', context)