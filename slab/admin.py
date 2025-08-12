from django.contrib import admin
from .models import Slab,UserSlab,EarningHistory

@admin.register(Slab)
class SlabAdmin(admin.ModelAdmin):
    list_display = ('slab_name', 'slab_percentage', 'max_amount', 'activate_status')
    list_editable = ('slab_percentage', 'max_amount', 'activate_status')
    search_fields = ('slab_name',)
    list_filter = ('activate_status',)

@admin.register(UserSlab)
class UserSlabAdmin(admin.ModelAdmin):
    list_display = ('user', 'slab')
    search_fields = ('user__username', 'slab__slab_name')


@admin.register(EarningHistory)
class EarningHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'earning_type', 'earning_amount', 'currency', 'earning_from', 'datetime')
    search_fields = ('user__username', 'earning_type', 'earning_from')
    list_filter = ('earning_type', 'currency')
