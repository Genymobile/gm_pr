from gm_pr import settings

def proj_repo(request):
    """ Retrieve project list from a Slack request or web request.
    Parameter come from GET and can be either 'channel_name' or 'project' (they
    both give the same result)
    return a tuple: list of projects, channel name
    """
    repos = None
    project = None
    if request.GET != None and \
       'channel_name' in request.GET or 'project' in request.GET:
        if 'channel_name' in request.GET:
            project = request.GET['channel_name']
        else:
            project = request.GET['project']

        if project in settings.PROJECTS_REPOS:
            repos = settings.PROJECTS_REPOS[project]
    return project, repos
