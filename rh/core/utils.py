from notifications import signals

def upload_directory_file(instance, filename):
    return '{0}/{1}/{2}'.format(instance._meta.app_label, instance._meta.model_name, filename)

def notify(_from, _to, _subject, _message, obj):
    return signals.notify.send(**{
        'sender': _from,
        'actor': _from,
        'recipient': _to,
        'verb': _subject,
        'action_object': obj,
        'target': obj,
        'level': 'info',
        'description': _message,
        'public': False,
        'url': obj.get_absolute_url()
    })