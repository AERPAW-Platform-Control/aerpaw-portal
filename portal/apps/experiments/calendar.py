import calendar, datetime
from datetime import datetime, timedelta

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiments.models import ScheduledSession


_MONTHS = {
    1: 'Janruary',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

_WEEKDAYS = {
    0: 'Sunday',
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
}

class SandboxCalendar():
    
    sandbox_calendar = calendar.TextCalendar(firstweekday=0)
    current_datetime = datetime.now()
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_month_name = datetime.now().strftime("%B")
    current_day = datetime.now().day
    current_weekday_number = datetime.now().weekday()
    current_day_name = datetime.now().strftime("%A")
    
    def next_monthrange(self):
        """  
        Determines how many days are in the following month
        """
        try:
            if self.current_month != 12:
                days_in_next_month = calendar.monthrange(self.current_year, self.current_month+1)
            else:
                days_in_next_month = calendar.monthrange(self.current_year +1, 1)
            return days_in_next_month
        except Exception as exc:
            new_error(exc, user=None)
    
    def next_month_number_name(self):
        """
        Determines the following month's name and number  
        """
        try:
            if self.current_month != 12:
                next_month_number = self.current_month+1
                next_month_name =  _MONTHS[self.current_month+1]
            else:
                next_month_number = 1
                next_month_name =  _MONTHS[1]
            return next_month_number, next_month_name
        except Exception as exc:
            new_error(exc, user=None)
    
    def days_left_in_month(self):
        """  
        Calculates how many days are left in the month from today
        """
        return calendar.monthrange(self.current_year, self.current_month)[1] - self.current_day
    
    def days_required_from_next_month(self):
        """  
        Calculates how many days are needed in the following month
            = 30 - number of days left from today to end of this month
        """
        return 30 - calendar.monthrange(self.current_year, self.current_month)[1] - self.current_day
    
    def begin_week_with_sunday(self, day: int) -> int:
        """  
        Converts the day that represents a week that starts with Monday  
        (0 = Monday, 1 = Tuesday, etc ...)
        
        to a day where the week starts with Sunday 
        (0 = Sunday, 1 = Monday etc...)
        """
        new_day_index = 0
        try:
            if day < 6:
                new_day_index = day+1
        except Exception as exc:
            new_error(exc, user=None)
        return new_day_index

    def create_calendar_month(self, year:int =None, month:int =None ) -> dict:
        """ 
        Creates a calendar for one of the months for scheduling the sandbox sessions
        calendar.weekday() returns 0 for Monday and 6 for Sunday
        """
        try:
            days_in_month = {day:[] for index, day in _WEEKDAYS.items()}
            if year == None:
                year = self.current_year
            if month == None:
                month = self.current_month
                month_name = self.current_month_name
            else:
                month_name = _MONTHS[month]

            active_sandbox_sessions = ScheduledSession.objects.filter(session_type='sandbox', is_active=True, scheduled_start__isnull=False, scheduled_start__month=month, scheduled_start__year=year)
            
            first_day = calendar.weekday(year, month, 1)
            first_day_index = self.begin_week_with_sunday(first_day)
            last_day_to_register = (datetime.now() + timedelta(days=28)).day
            for index, day in enumerate(days_in_month.keys()):
                if first_day_index > index:
                    days_in_month[day].append(('00', False))

            for day in range(1, calendar.monthrange(year, month)[1]+1):
                day_number = self.begin_week_with_sunday(calendar.weekday(year, month, day))
                is_reserved = False
                out_of_bounds = False
                for session in active_sandbox_sessions:
                    scheduled_session = range(session.scheduled_start.day, session.scheduled_end.day)
                    for scheduled_day in scheduled_session:
                        if scheduled_day == day:
                            is_reserved = True
                if day <= self.current_day and month == self.current_month:
                    out_of_bounds = True
                if day > last_day_to_register and month != self.current_month:
                    out_of_bounds = True
                    
                day = str(day) if len(str(day)) == 2 else f'0{str(day)}'
                days_in_month[_WEEKDAYS[day_number]].append((day, is_reserved, out_of_bounds))
            
            weeks_in_month = 0
            for weekday, days in days_in_month.items():
                if len(days) > weeks_in_month:
                    weeks_in_month = len(days)
            for weekday, days in days_in_month.items():
                if len(days) < weeks_in_month:
                    days_in_month[weekday].append(('00', False))
            
            return {month_name:( year, month, days_in_month)}
        except Exception as exc:
            new_error(exc, user=None)

    def get_calendar(self):
        try:
            next_month_number, next_month_name = self.next_month_number_name()
            next_year = self.current_year
            if next_month_number == 1:
                next_year = self.current_year+1
            
            current_calendar = self.create_calendar_month()
            next_month_calendar = self.create_calendar_month(year=next_year, month=next_month_number)
            return current_calendar | next_month_calendar
        except Exception as exc:
            new_error(exc, user=None)
    
    