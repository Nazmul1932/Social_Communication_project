from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ProfileModelForm
from django.views.generic import ListView,DetailView
from django.contrib.auth.models import User


def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None,request.FILES or None,instance=profile)
    confirm = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }
    return render(request, 'profiles/my_profile.html', context)


def invites_received(request):
    profile = Profile.objects.get(user=request.user)
    queryset = Relationship.objects.invitations_received(profile)
    results = list(map(lambda x: x.sender, queryset))
    is_empty = False
    if len(results) == 0:
        is_empty = True
    context = {
        'queryset': results,
        'is_empty': is_empty,
    }
    return render(request, 'profiles/invite_received.html', context)


def accept_invitation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:invites_received_view')


def reject_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:invites_received_view')


def invites_profiles_list(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)
    context = {
        'qs':qs,
    }
    return render(request, 'profiles/invites_profile_list.html', context)


def profiles_list(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)
    context = {
        'qs':qs,
    }
    return render(request, 'profiles/profile_list.html', context)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        relationship_receive = Relationship.objects.filter(sender=profile)
        relationship_send = Relationship.objects.filter(receiver=profile)
        relationship_receiver = []
        relationship_sender = []

        for item in relationship_receive:
            relationship_receiver.append(item.receiver.user)
        for item in relationship_send:
            relationship_sender.append(item.sender.user)

        context['relationship_receiver'] = relationship_receiver
        context['relationship_sender'] = relationship_sender
        context['posts'] = self.get_object().get_all_authors_post()
        context['len_posts'] = True if len(self.get_object().get_all_authors_post()) > 0 else False
        return context



class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    # context_object_name = 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        relationship_receive = Relationship.objects.filter(sender=profile)
        relationship_send = Relationship.objects.filter(receiver=profile)
        relationship_receiver = []
        relationship_sender = []

        for item in relationship_receive:
            relationship_receiver.append(item.receiver.user)

        for item in relationship_send:
            relationship_sender.append(item.receiver.user)

        context['relationship_receiver'] = relationship_receiver
        context['relationship_sender'] = relationship_sender
        context['is_empty'] = False

        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context


def send_invitation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile')


def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile')
