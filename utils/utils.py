import datetime

def get_formatted_time(format_string):
        try:
            current_time = datetime.datetime.now()
            test_time = current_time.strftime(
                format_string
            )
            return test_time
        except ValueError:
            return None