from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as SigninView
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm, UserSettingsForm, MyPasswordChangeForm
from core.models import Post
from core.views import safe_next
from .models import User

# ---------------------------
# Class-based views
# ---------------------------

class SignUpView(CreateView):
    template_name = 'account/signup.html'
    success_url = reverse_lazy('home')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        return response

class LoginView(SigninView):
    template_name = 'account/login.html'
    success_url = reverse_lazy('home')
    form_class = UserLoginForm
    success_message = "Successfully logged in"

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/profile.html'

    def get_object(self, **kwargs):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['object']
        context['posts'] = Post.objects.get_user_posts(user)
        context['is_following'] = self.request.user.is_following(user)
        return context

class SettingsView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'account/settings.html'
    success_url = reverse_lazy('settings')
    form_class = UserSettingsForm

    def get_object(self, **kwargs):
        return self.request.user

# ---------------------------
# Function-based views
# ---------------------------

@login_required
def PasswordChangeView(request):
    if request.method == 'POST':
        password_form = MyPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated')
            return redirect('settings')
    else:
        password_form = MyPasswordChangeForm(request.user)

    return render(request, 'account/password.html', {'form': password_form})

@login_required
def LogoutView(request):
    logout(request)
    return redirect('login')

@login_required
@require_POST
def follow(request):
    username = request.POST.get('username')

    if username:
        user_to_follow = get_object_or_404(User, username=username)
        request.user.toggle_follow(user_to_follow)

    return HttpResponseRedirect(safe_next(request))


@login_required
def follow_list(request, username, kind):
    """The people following `username` (kind='followers') or the people
    they follow (kind='following')."""
    user = get_object_or_404(User, username=username)
    people = user.followed_by.all() if kind == 'followers' else user.follows.all()
    return render(request, 'account/follow_list.html', {'profile_user': user, 'people': people, 'kind': kind})


# Same extensions the model field itself validates against (account/models.py)
# — reused here so this endpoint rejects bad uploads before they ever touch
# the model, since a plain setattr()+save() (below) does NOT run model
# validators the way a ModelForm would.
_image_extension_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])


@login_required
@require_POST
def upload_image(request):
    """Handles the avatar/background drag-and-drop uploader on the profile
    page (see static/js/profile.js) -- a plain AJAX endpoint, not a form."""
    if 'profile_img' in request.FILES:
        field_name = 'profile_img'
    elif 'background_img' in request.FILES:
        field_name = 'background_img'
    else:
        return JsonResponse({'error': 'No image file provided'}, status=400)

    uploaded_file = request.FILES[field_name]
    try:
        _image_extension_validator(uploaded_file)
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)

    setattr(request.user, field_name, uploaded_file)
    request.user.save(update_fields=[field_name])
    return JsonResponse({'ok': True})