from django.db import models
from django.utils.text import slugify

# Categories (moved before Blog to avoid forward reference issues)
class Categories(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):  # Fixed: was missing underscores
        return self.name

# Tags
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):  # Fixed: was missing underscores
        return self.name

# Blogs
class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')
    categories = models.ManyToManyField(Categories, blank=True, related_name='blogs')
    tags = models.ManyToManyField(Tag, blank=True, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # Fixed: was missing underscores
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.title:
                self.slug = slugify(self.title)
            else:
                self.slug = f"blog-{self.id}"
            original_slug = self.slug
            queryset = Blog.objects.all().filter(slug__iexact=self.slug).exists()
            count = 1
            while queryset:
                self.slug = f'{original_slug}-{count}'
                count += 1
                queryset = Blog.objects.all().filter(slug__iexact=self.slug).exists()
        super().save(*args, **kwargs)

# Comments
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    likes = models.ManyToManyField('auth.User', related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):  # Fixed: was missing underscores
        return f'Comment by {self.name} on {self.blog}'