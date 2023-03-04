from django.shortcuts import render, redirect
from .forms import ConversationForm
from .models import Conversation

def create_conversation(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = Conversation(text=form.cleaned_data['text'])
            conversation.save()
            return redirect('create_conversation')
    else:
        form = ConversationForm()
    return render(request, 'create_conversation.html', {'form': form})