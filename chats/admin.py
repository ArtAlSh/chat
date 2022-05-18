from django.contrib import admin
from .models import ListOfChats


class ChatListInline(admin.TabularInline):
    model = ListOfChats
    extra = 0


class ChatAdmin(admin.ModelAdmin):
    inlines = [ChatListInline]


# Register your models here.
