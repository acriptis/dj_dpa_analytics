import json
from django.contrib import admin

from dialogs.models import Dialog, Author, Utterance, Annotation, UtteranceHypothesis
from django.template.loader import render_to_string

class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "__str__", "user_telegram_id"
    )
admin.site.register(Author, AuthorAdmin)


class UtteranceInline(admin.TabularInline):
    model = Utterance
    # raw_id_fields = ("parent_utterance",)
    # extra = 0

class DialogAdmin(admin.ModelAdmin):
    list_display = (
        'get_author',
        # 'human',
        'start_time', 'rating')

    def get_author(self, obj):
        return obj.human.user_telegram_id

    get_author.short_description = 'Author'

    fields = ('conversation_id', 'start_time', 'human', 'view_dialog', 'rating')
    readonly_fields = ('conversation_id', 'start_time', 'rating', 'human', 'view_dialog')
    search_fields = ['dp_id', 'conversation_id']
    list_filter = ('rating',)
    ordering = ('-start_time',)

    def view_dialog(self, obj):
        return render_to_string('admin/dialog_view.html', {'dialog_json': obj.dialog_json})
    # def view_dialog(self, obj):
    #     return str(obj)
    view_dialog.short_description = 'Dialog view'
    view_dialog.allow_tags = True
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
