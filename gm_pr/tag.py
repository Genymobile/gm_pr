from enum import Enum

class Tag(Enum):
    """ Different GithubFragment type
    """
    DETAILS = "details"
    LABELS = "labels"
    INFO = "info"
    COMMENTS = "comments"
    REVIEWS = "reviews"
    REVIEW_COMMENTS = "review_comments"
    EVENTS = "events"
    COMMITS = "commits"
