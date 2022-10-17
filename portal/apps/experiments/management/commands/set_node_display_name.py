from django.core.management.base import BaseCommand, CommandError

from portal.apps.experiments.models import CanonicalExperimentResource


def set_default_node_display_name():
    canonical_experiment_resources = CanonicalExperimentResource.objects.all()
    for cer in canonical_experiment_resources:
        try:
            if not cer.node_display_name:
                cer.node_display_name = cer.resource.name
                cer.save()
        except Exception as e:
            print(e)


class Command(BaseCommand):
    help = 'Set node_display_name if NULL'

    def handle(self, *args, **kwargs):
        try:
            set_default_node_display_name()

        except Exception as e:
            print(e)
            raise CommandError('Initalization failed.')
