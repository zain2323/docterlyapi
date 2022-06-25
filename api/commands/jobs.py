from api.commands import commands
from api.models import Slot, BookedSlots, Event, EventMeta
from datetime import datetime, timedelta

@commands.cli.command()
def create_scheduled_events():
    """Create events for the doctor's slot"""
    slots = Slot.query.all()
    for slot in slots:
        # get day. start and end time
        day = slot.day
        start = slot.start
        end = slot.end
        # Getting next date of the appointment
        current_date = datetime.now().date()
        current_time = datetime().now().time()
        next_date = next_weekday(current_date, day.id)
        # Fetching current date of the appointment
        event = slot.get_latest_event()
        current_occurring_date = event.occurring_date
        # If the current date is equal to the next date then we only need to create new event when there is some time left.
        # If they are not equal and the next date is greater than the current date, then this means
        # we need to create new event    
        if (current_occurring_date < next_date) or (current_occurring_date == next_date and end < current_time):
            # Fetch the current event meta
            event_meta = event.get_event_meta()
            interval = event_meta.repeat_interval
            start_date = event_meta.start_date
            # Generating the new date
            new_date = (current_date - start_date) + interval
            # Creating the new event
            new_event = Event(occurring_date=new_date, slot=slot)
            db.session.add(new_event)
            # Creating the new booked slot
            new_booked_slot = BookedSlots(event=new_event)
            db.session.add(new_booked_slot)
            db.session.commit()

def next_weekday(date, weekday):
    days_ahead = weekday - date.isoweekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + timedelta(days_ahead)   

