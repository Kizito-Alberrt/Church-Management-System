from django.db import migrations
from church.models import Province, District

def assign_districts(apps, schema_editor):
    User = apps.get_model('church', 'User')
    Province = apps.get_model('church', 'Province')
    District = apps.get_model('church', 'District')

    # Ensure a default province exists
    province, _ = Province.objects.get_or_create(
        name="Default Province",
        defaults={'code': 'DP'}
    )

    # Assign districts to Main Reverends
    for rev in User.objects.filter(role='MAIN_REVEREND'):
        if not District.objects.filter(main_reverend=rev).exists():
            District.objects.create(
                name=f"{rev.get_full_name() or rev.username}'s District",
                province=province,
                main_reverend=rev
            )

class Migration(migrations.Migration):
    dependencies = [
        ('church', '0001_initial'),  # Replace with your last migration
    ]
    operations = [
        migrations.RunPython(assign_districts),
    ]