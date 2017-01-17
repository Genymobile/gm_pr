class PullRequest:
    """ Simple class wrapper for PullRequest properties
    """
    def __init__(self, url="", title="", updated_at="", user="", my_open_comment_count=0,
                 last_activity=None, repo="",
                 nbreview=0, feedback_ok=0, feedback_ko=0,
                 milestone=None, labels=None, is_old=False):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.my_open_comment_count = my_open_comment_count
        self.last_activity = last_activity
        self.repo = repo
        self.nbreview = nbreview
        self.feedback_ok = feedback_ok
        self.feedback_ko = feedback_ko
        self.milestone = milestone
        self.labels = labels
        self.is_old = is_old
