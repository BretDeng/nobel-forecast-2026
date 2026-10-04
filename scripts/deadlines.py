"""2026 official announcement times and one-hour prediction cutoffs."""
from datetime import datetime, timedelta, timezone

SOURCE = 'https://www.nobelprize.org/prizes/about/prize-announcement-dates/'
ANNOUNCEMENTS = {
    'medicine': '2026-10-05T09:30:00+00:00',
    'physics': '2026-10-06T09:45:00+00:00',
    'chemistry': '2026-10-07T09:45:00+00:00',
    'literature': '2026-10-08T11:00:00+00:00',
    'economics': '2026-10-12T09:45:00+00:00',
}

def utc_now():
    return datetime.now(timezone.utc)

def cutoff(category):
    return datetime.fromisoformat(ANNOUNCEMENTS[category]) - timedelta(hours=1)

def is_open(category, now=None):
    return (now or utc_now()) < cutoff(category)

def metadata(category):
    return {'announcementAt': ANNOUNCEMENTS[category],
            'predictionFreezeAt': cutoff(category).isoformat(),
            'announcementSource': SOURCE}
