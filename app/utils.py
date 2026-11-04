from datetime import datetime

def format_date(date_obj):
    """Format a datetime object into a readable string."""
    if not date_obj:
        return "—"
    return date_obj.strftime('%d %b %Y')

def format_datetime(date_obj):
    """Format a datetime object with time."""
    if not date_obj:
        return "—"
    return date_obj.strftime('%d %b %Y, %H:%M')

def get_status_badge_class(status):
    """Return Bootstrap badge class based on decision status."""
    status_map = {
        'Draft': 'bg-secondary',
        'Recorded': 'bg-primary',
        'Implemented': 'bg-info',
        'Under Review': 'bg-warning text-dark',
        'Closed': 'bg-success'
    }
    return status_map.get(status, 'bg-secondary')

def get_outcome_badge_class(result):
    """Return Bootstrap badge class based on outcome result."""
    result_map = {
        'Good': 'bg-success',
        'Neutral': 'bg-secondary',
        'Bad': 'bg-danger'
    }
    return result_map.get(result, 'bg-secondary')

def calculate_percentage(part, whole):
    """Safely calculate percentage."""
    if whole == 0:
        return 0
    return round((part / whole) * 100, 1)