from django.contrib import messages
from django.shortcuts import render, redirect
from .models import *
from profiles.models import *
from .forms import PostModelForm, CommentModelForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse


def post_comment_create_and_list_view(request):
    queryset = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    post_form = PostModelForm()
    comment_form = CommentModelForm()
    post_added = False

    profile = Profile.objects.get(user=request.user)

    if 'submit_post_form' in request.POST:
        print(request.POST)
        post_form = PostModelForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            post_form = PostModelForm()
            post_added = True

    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            comment_form = CommentModelForm()

    context = {
        'queryset': queryset,
        'profile': profile,
        'post_form': post_form,
        'comment_form': comment_form,
        'post_added': post_added,
    }

    return render(request, 'posts/main.html', context)


def like_unlike_post_view(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)
        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)
        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)
        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Like'

            post_obj.save()
            like.save()
        data = {
            'value': like.value,
            'likes': post_obj.liked.all().count()
        }
        return JsonResponse(data, safe=False)

    return redirect('posts:post_comment_create_and_list')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/delete.html'
    success_url = reverse_lazy('posts:post_comment_create_and_list')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'You need to be the author of the post in order to delete it')
        return obj


class PostUpdateView(UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/update.html'
    success_url = reverse_lazy('posts:post_comment_create_and_list')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, "You need to be the author of the post in order to update it")
            return super().form_invalid(form)


