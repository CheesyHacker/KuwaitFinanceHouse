from django.contrib import admin

# Register your models here.
from  .models import Actions, Approvals, Criticality, Documents, Records, Employees


admin.site.register(Actions)
admin.site.register(Approvals)
admin.site.register(Records)
admin.site.register(Documents)
admin.site.register(Criticality)
admin.site.register(Employees)