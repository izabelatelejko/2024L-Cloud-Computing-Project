def decide_time_of_day(hour: int):
    if hour <  6:
        return 'night'
    elif hour < 12:
        return 'morning'
    elif hour < 18:
        return 'afternoon'
    elif hour < 22:
        return 'evening'
    else: return 'night'