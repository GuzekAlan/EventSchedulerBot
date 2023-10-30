from datetime import datetime
from collections import Counter


def pick_date(avalibilities: list()) -> datetime or None:
    print(avalibilities)
    no_datetimes = []
    ok_datetimes = []
    maybe_datetimes = []
    for user_dict in avalibilities:
        dates_dict = list(user_dict.values())[0]
        for _, availibility_dict in dates_dict.items():
            no_datetimes.extend(availibility_dict["no"])
            ok_datetimes.extend(availibility_dict["ok"])
            maybe_datetimes.extend(availibility_dict["maybe"])
    if git_times := [i for i in ok_datetimes if i not in no_datetimes]:
        if len(git_times) > 0:
            try:
                return Counter(git_times).most_common(1)[0][0]
            except:
                return git_times[0]
    if git_times := [i for i in maybe_datetimes if i not in no_datetimes]:
        if len(git_times) > 0:
            try:
                return Counter(git_times).most_common(1)[0][0]
            except:
                return git_times[0]
    else:
        return None
