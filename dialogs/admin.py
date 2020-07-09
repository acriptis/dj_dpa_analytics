from django.contrib import admin

# Register your models here.
from django.contrib import admin
from dialogs.models import Dialog, Author, Utterance, Annotation, UtteranceHypothesis

class AuthorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Author, AuthorAdmin)


class UtteranceInline(admin.TabularInline):
    model = Utterance
    # raw_id_fields = ("parent_utterance",)
    # extra = 0

class DialogAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_time', 'rating')
    # inlines = [
    #     UtteranceInline,
    # ]
    fields = ('conversation_id', 'dp_id', 'start_time', 'rating', 'human', 'bot', 'view_dialog')
    readonly_fields = ('conversation_id', 'dp_id', 'start_time', 'rating', 'human', 'bot', 'view_dialog')
    search_fields = ['dp_id', 'conversation_id']
    list_filter = ('rating',)
    ordering = ('-start_time',)

    def view_dialog(self, obj):
        return str(obj)

    view_dialog.empty_value_display = '???'

admin.site.register(Dialog, DialogAdmin)

class DialogInline(admin.TabularInline):
    model = Dialog
#     # raw_id_fields = ("parent_utterance",)
#     # extra = 0


class AnnotationInline(admin.TabularInline):
    model = Annotation
    raw_id_fields = ("parent_utterance",)
    extra = 0


class UtteranceHypothesesInline(admin.TabularInline):
    model = UtteranceHypothesis
    raw_id_fields = ("parent_utterance",)
    readonly_fields = ("parent_utterance",)
    extra = 0
    inlines = [
        UtteranceInline,
    ]

class UtteranceAdmin(admin.ModelAdmin):
    inlines = [
        AnnotationInline,
        UtteranceHypothesesInline
    ]
    raw_id_fields = ('parent_dialog', 'author')
    readonly_fields = ("parent_dialog", "author")
    list_display = ('text', 'author', 'timestamp')

admin.site.register(Utterance, UtteranceAdmin)


class UtteranceHypothesisAdmin(admin.ModelAdmin):
    readonly_fields = ('parent_utterance', 'text', 'skill_name', 'confidence', 'other_attrs')
admin.site.register(UtteranceHypothesis, UtteranceHypothesisAdmin)

class AnnotationAdmin(admin.ModelAdmin):
    readonly_fields = ('parent_utterance', 'annotation_type', 'annotation_dict')
admin.site.register(Annotation, AnnotationAdmin)
