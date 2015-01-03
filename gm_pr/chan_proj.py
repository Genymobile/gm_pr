from gm_pr import settings

def chan_proj(request):
    """ Retrieve project list from a Slack request or web request
    return a tuple: list of projects, channel name
    """
    projects = None
    channel = None
    if request.GET != None and 'channel_name' in request.GET:
        channel = request.GET['channel_name']
        if channel in settings.PROJECTS_CHAN:
            projects = settings.PROJECTS_CHAN[channel]
    return projects, channel
