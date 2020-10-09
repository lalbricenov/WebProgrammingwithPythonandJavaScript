from django.shortcuts import render
from django import forms
from . import util
from django.urls import reverse
from django.http import HttpResponseRedirect
import markdown2
import datetime
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import random
# This is a type of widged derived from the DateInput widget inside forms.
# The only difference is that the type of the input is 'date'. That means that
# the interface for selecting dates of html5 will be used. https://www.youtube.com/watch?v=I2-JYxnSiB0
# class DateInput(forms.DateInput):
#     input_type = 'date'


# class DateTimeInput(forms.DateTimeInput):
#     input_type = 'datetime-local'


def validateUniqueTitle(title):
    entryNames = util.entry_names()
    if title.lower() in entryNames.keys():
        raise ValidationError(
            _('The title \"%(title)s\" is already in use'), params={'title': title})


class PageForm(forms.Form):
    # The available fields can be found in https://docs.djangoproject.com/en/3.1/ref/forms/fields/
    # The default widget used for each field will be ok most of the time. However, if you want to use a different widget you can go to https://docs.djangoproject.com/en/3.1/ref/forms/widgets/ and find the appropiate widget
    title = forms.CharField(max_length=150, label="Title", validators=[validateUniqueTitle, RegexValidator('^[a-zA-Z0-9 _\-.]*$',
                                                                                                           message='Title must contain only letters, numbers _ - or .'
                                                                                                           )])
    content = forms.CharField(widget=forms.Textarea)
    # fecha = forms.DateField(widget=DateInput, initial=datetime.date.today, help_text='100 characters max.')
    # fechaHora = forms.DateTimeField(widget=DateTimeInput)


class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def search(request):
    # entry_names returns a dictionary with the names of the files in lowercase as the keys, and the names as they are in the file system as values
    entryNames = util.entry_names()
    query = request.GET['q'].lower()
    if query in entryNames.keys():
        # If the entry exists
        return HttpResponseRedirect(reverse("entry",  kwargs={'title': query}))
    else:
        # Find all the entries that have a substring that corresponds to the query
        results = []
        for entry in entryNames.keys():
            if entry.find(query) != -1:
                results.append(entryNames[entry])
        return render(request, "encyclopedia/searchResults.html", {
            "entries": results,
            "query": query
        })


def entry(request, title):
    entryNames = util.entry_names()

    if title.lower() in entryNames.keys():
        # If the title of the entry exists in the list of titles
        # This gets the name with the correct capitalization
        name = entryNames[title.lower()]
        content = util.get_entry(name)
        content = markdown2.markdown(content)
        return render(request, "encyclopedia/entry.html", {
            "content": content,
            "title": entryNames[title.lower()]
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "The requested page was not found"
        })


def create(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            util.save_entry(data["title"], data['content'])
            # mdFile = open(f'entries/{data["title"]}.md', 'w')
            # mdFile.write(data['content'])
            # mdFile.close()

            return HttpResponseRedirect(reverse("entry",  kwargs={'title': data['title']}))
    else:
        form = PageForm()
    return render(request, "encyclopedia/create.html", {
        "form": form
    })


def edit(request, title):
    if request.method == 'POST':
        form = EditPageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            util.save_entry(title, data['content'])
            return HttpResponseRedirect(reverse("entry",  kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
            })
    else:
        entryNames = util.entry_names()
        # If the entry exists
        if title.lower() in entryNames.keys():
            # Edition interface
            data = {'content': util.get_entry(title)}
            form = EditPageForm(data)
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
            })
        else:
            # The entry does not exist yet
            return render(request, "encyclopedia/error.html", {
                "error": "The requested page was not found"
            })


def randomEntry(request):
    entryNames = util.entry_names()
    title = random.choice(list(entryNames.values()))
    return HttpResponseRedirect(reverse("entry",  kwargs={'title': title}))
