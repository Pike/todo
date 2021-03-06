from django import forms
from life.models import Locale
from todo.models import Project, ProtoTask, ProtoTracker, Tracker

class ProtoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, proto):
        return "%s (%s)" % (proto.summary, proto.suffix)

class ProjectChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, project):
        return "%s (%s)" % (project.label, project.code)

class LocaleMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, locale):
        return "%s / %s" % (locale.code, locale.name)

class TrackerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, tracker):
        return "%d: %s (%s) %s + %s" % (tracker.pk, tracker.summary,
                                        tracker.alias, tracker.project,
                                        tracker.locale)

class ChooseParentForm(forms.Form):
    "Form used to choose an existing parent tracker or create a new one."

    _q = Tracker.objects.select_related('project', 'locale').all()
    tracker = TrackerChoiceField(label='Existing parent tracker',
                                queryset=_q, required=False,
                                help_text="OR create a new one:")
    parent_summary = forms.CharField(label='Summary', max_length=200,
                                     required=False)
    parent_project = ProjectChoiceField(queryset=Project.objects.all(),
                                     required=False)
    parent_locale = forms.ModelChoiceField(queryset=Locale.objects.all(),
                                    required=False, help_text="Probably better"
                                    " to leave this empty." )
    parent_suffix = forms.SlugField(label='Alias suffix', max_length=8,
                                    required=False, help_text="Will be "
                                    "appended to project's alias. "
                                    "Good example: '-newloc'; result: "
                                    "'fx40-newloc'.")

    def clean(self):
        clean = self.cleaned_data
        if clean['parent_summary'] and not clean['parent_project']:
            raise forms.ValidationError("Specify at least a summary and a "
                                        "project to create a new tracker.")
        return clean

class AddTasksForm(forms.Form):
    prototype = ProtoChoiceField(queryset=ProtoTask.objects.all())
    summary = forms.CharField(label='Summary', max_length=200, required=False,
                              help_text="Leave empty to use the prototype's "
                              "summary.")
    project = ProjectChoiceField(queryset=Project.objects.all())
    locales = LocaleMultipleChoiceField(queryset=Locale.objects.all(),
                                        required=False)
    suffix = forms.SlugField(label='Alias suffix', max_length=8,
                             required=False, help_text="Will be appended to "
                             "parent's or project's alias. Good example: "
                             "'-search'. Leave empty to use the prototype's "
                             "suffixi (recommended).")
    bugid = forms.IntegerField(label='Bug id', required=False,
                               help_text="Almost certainly better to leave "
                               "this empty. If you put an ID, it will be "
                               "inherited by all the tasks and trackers you're"
                               " creating, taking precedence over the alias "
                               "mechanics.")

class AddTrackersForm(AddTasksForm):
    prototype = ProtoChoiceField(queryset=ProtoTracker.objects.all())

class UpdateTodoForm(forms.Form):
    summary = forms.CharField(max_length=200, required=True)
    bug = forms.CharField(max_length=200, required=False)

    def clean_bug(self):
        # the input value is a string, because it may be an ID or an alias.
        # do the intelogent thing here, and convert the ID to an integer.
        bug = self.cleaned_data['bug']
        if not bug:
            return None
        try:
            bug = int(bug)
        except ValueError:
            # it's a string!
            pass
        return bug

class ResolveTaskForm(forms.Form):
    redirect_url = forms.CharField()

class ResolveSimpleStepForm(forms.Form):
    redirect_url = forms.CharField()
    
class ResolveReviewStepForm(forms.Form):    
    redirect_url = forms.CharField()
    success = forms.BooleanField(required=False)
    failure = forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        success = cleaned_data.get("success")
        failure = cleaned_data.get("failure")
        if not success and not failure:
            raise forms.ValidationError("A resolution needs to be specified"
                                        "for review todos.")
        return cleaned_data
