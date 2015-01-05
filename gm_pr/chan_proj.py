from gm_pr import settings

def chan_proj(request):
    """ Retrieve project list from a Slack request or web request.
    Parameter come from GET and can be either 'channel_name' or 'project' (they
    both give the same result)
    return a tuple: list of projects, channel name
    """
    projects = None
    channel = None
    if request.GET != None and \
       'channel_name' in request.GET or 'project' in request.GET :
        if 'channel_name' in request.GET:
            channel = request.GET['channel_name']
        else:
            channel = request.GET['project']

        if channel in settings.PROJECTS_CHAN:
            projects = settings.PROJECTS_CHAN[channel]
    return projects, channel
