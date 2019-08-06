from django.contrib import admin
from .models import Tool, Tag, CommandLineArgument


class ArgumentsAdmin(admin.TabularInline):
    model = Tool.arguments.through


# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'html_name', 'created_by', 'short_description', 'description', 'path', 'script_name', 'command_line', 'status', 'visuel', 'tags']}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ArgumentsAdmin,]

admin.site.register(Tool, ToolsAdmin)
admin.site.register(Tag)
admin.site.register(CommandLineArgument)

