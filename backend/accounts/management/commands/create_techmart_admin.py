import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import UserRoleProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update TechMart primary super admin (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=os.getenv('ADMIN_DEFAULT_USERNAME', 'techmart_admin'))
        parser.add_argument('--email', default=os.getenv('ADMIN_DEFAULT_EMAIL', ''))
        parser.add_argument('--password', default=os.getenv('ADMIN_DEFAULT_PASSWORD', ''))

    def handle(self, *args, **options):
        username = (options['username'] or '').strip()
        email = (options['email'] or '').strip().lower()
        password = options['password'] or ''

        if not username:
            raise CommandError('Username required. Pass --username or ADMIN_DEFAULT_USERNAME.')
        if not email:
            raise CommandError('Email required. Pass --email or ADMIN_DEFAULT_EMAIL.')
        if not password:
            raise CommandError('Password required. Pass --password or ADMIN_DEFAULT_PASSWORD.')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        profile, _ = UserRoleProfile.objects.get_or_create(user=user)
        profile.role = UserRoleProfile.ROLE_ADMIN
        profile.save(update_fields=['role'])

        verb = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{verb} super admin "{username}" ({email}).'))
