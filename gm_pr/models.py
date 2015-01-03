class Pr:
    """ Stupid class wrapper for pr properties
    """
    def __init__(self, url="", title="", updated_at="", user="",
                 repo="", nbreview=0):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.repo = repo
        self.nbreview = nbreview


