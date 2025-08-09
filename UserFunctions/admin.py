from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'userid',
        'name',
        'email',
        'usercode',
        'refarcode',
        'is_active',
        'is_admin',
    )

    list_filter = ('is_active', 'is_admin')
    search_fields = ('userid', 'name', 'email', 'usercode', 'refarcode')
    ordering = ('userid',)

    # Fields to show in the add/edit form
    fields = (
        'userid',
        'name',
        'email',
        'password',
        'usercode',
        'refarcode',
        'is_active',
        'is_admin',
    )

    readonly_fields = ('usercode',)  # usercode auto-generated, no manual edit

    # Use this to display password hash properly
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing user
            return self.readonly_fields + ('password',)
        return self.readonly_fields

    # Optional override to hash password when saving in admin
    def save_model(self, request, obj, form, change):
        # If password field is in raw form, hash it
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
