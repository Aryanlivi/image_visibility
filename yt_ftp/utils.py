from datetime import datetime
import pytz
def get_current_datetime(timezone_str="Asia/Kathmandu"):
    tz=pytz.timezone(timezone_str)
    return datetime.now(tz=tz).replace(second=0,microsecond=0)


def wait_for_next_10_minute_interval():
    current_time =get_current_datetime()

    # Calculate how many minutes past the last 10-minute mark
    minutes_past = current_time.minute % 10

    # Calculate the next 10-minute interval, ensuring seconds are set to 00
    if minutes_past == 0:
        next_interval = current_time.replace(second=0, microsecond=0)  # Already at the correct 10-minute mark
    else:
        # Adjust the time to the next 10-minute interval and set seconds and microseconds to 00
        next_interval = (current_time + timedelta(minutes=(10 - minutes_past))).replace(second=0, microsecond=0)

    # Wait until the next 10-minute mark
    wait_time = ((next_interval - current_time).total_seconds())+20
    logger.info(f"Waiting for {wait_time} seconds to reach the next 10-minute interval... i.e {next_interval}")
    time.sleep(wait_time)
    
