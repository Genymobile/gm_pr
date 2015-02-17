class Pr:
    """ Stupid class wrapper for pr properties
    """
    def __init__(self, url="", title="", updated_at="", user="",
                 repo="", nbreview=0, plusone=0, lgtm=0, milestone=None, labels=None,
                 is_old=False):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.repo = repo
        self.nbreview = nbreview
        self.plusone = plusone
        self.lgtm = lgtm
        self.milestone = milestone
        self.labels = labels
        self.is_old = is_old
