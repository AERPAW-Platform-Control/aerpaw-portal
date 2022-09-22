from django import template
from datetime import datetime, timezone
from portal.apps.experiments.models import AerpawExperiment, ExperimentSession

register = template.Library()


@register.filter
def id_to_experiment_name(experiment_id):
    try:
        experiment = AerpawExperiment.objects.get(pk=int(experiment_id))
        return experiment.name
    except Exception as exc:
        print(exc)
        return 'not found'


@register.filter
def session_running_time(session_id):
    try:
        session = ExperimentSession.objects.get(pk=int(session_id))
        if not session.start_date_time:
            return '0:00:00'
        else:
            delta = datetime.now(timezone.utc) - session.start_date_time
            return str(delta).split(".")[0]
    except Exception as exc:
        print(exc)
        return '0:00:00'
