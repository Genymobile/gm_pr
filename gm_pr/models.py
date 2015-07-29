class Pr:
    """ Stupid class wrapper for pr properties
    """
    def __init__(self, url="", title="", updated_at="", user="",
                 repo="", nbreview=0, feedback_ok=0, feedback_weak=0,
                 feedback_ko=0, milestone=None, labels=None,
                 is_old=False):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.repo = repo
        self.nbreview = nbreview
        self.feedback_ok = feedback_ok
        self.feedback_weak = feedback_weak
        self.feedback_ko = feedback_ko
        self.milestone = milestone
        self.labels = labels
        self.is_old = is_old
