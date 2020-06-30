# Copyright 2018-2020 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
from datetime import timezone

from streamlit.errors import StreamlitAPIException
from streamlit.js_number import JSNumber
from streamlit.js_number import JSNumberBoundsException
from streamlit.proto.Slider_pb2 import Slider

SUPPORTED_TYPES = {
    int: Slider.INT,
    float: Slider.FLOAT,
    datetime: Slider.DATETIME,
    date: Slider.DATE,
    time: Slider.TIME,
}
TIMELIKE_TYPES = (Slider.DATETIME, Slider.TIME, Slider.DATE)


def get_defaults(data_type, value):
    if data_type == Slider.INT:
        return {"min_value": 0, "max_value": 100, "step": 1, "format": "%d"}
    if data_type == Slider.FLOAT:
        return {
            "min_value": 0.0,
            "max_value": 1.0,
            "step": 0.01,
            "format": "%0.2f",
        }
    if data_type == Slider.DATETIME or data_type == Slider.DATE:
        return {
            "min_value": value[0] - timedelta(days=14),
            "max_value": value[0] + timedelta(days=14),
            "step": timedelta(days=1),
            "format": "YYYY-MM-DD",
        }
    if data_type == Slider.TIME:
        return {
            "min_value": time.min,
            "max_value": time.max,
            "step": timedelta(minutes=15),
            "format": "HH:mm",
        }


def _all_same_type(items):
    return len(set(map(type, items))) < 2


SECONDS_TO_MICROS = 1000 * 1000
DAYS_TO_MICROS = 24 * 60 * 60 * SECONDS_TO_MICROS


def _delta_to_micros(delta):
    return (
        delta.microseconds
        + delta.seconds * SECONDS_TO_MICROS
        + delta.days * DAYS_TO_MICROS
    )


UTC_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _datetime_to_micros(dt):
    # If dt is naive, Python converts from local time
    utc_dt = dt.astimezone(timezone.utc)
    return _delta_to_micros(utc_dt - UTC_EPOCH)


def _micros_to_datetime(micros, orig_tz):
    utc_dt = UTC_EPOCH + timedelta(microseconds=micros)
    # Convert from utc back to original time (local time if naive)
    return utc_dt.astimezone(orig_tz).replace(tzinfo=orig_tz)


def marshall_proto(element, label, min_value, max_value, value, step, format):
    """Megafunction that does the following:
    1. Validate user input and set appropriate defaults
    2. Serialize to the slider proto (basically, a list of floats)
    3. Return the info needed to deserialize back to the original types
    """

    # Set value default.
    if value is None:
        value = min_value if min_value is not None else 0

    # Ensure that the value is either a single value or a range of values.
    single_value = isinstance(value, tuple(SUPPORTED_TYPES.keys()))
    range_value = isinstance(value, (list, tuple)) and len(value) in (0, 1, 2)
    if not single_value and not range_value:
        raise StreamlitAPIException(
            "Slider value should either be an int/float/datetime or a list/tuple of "
            "0 to 2 ints/floats/datetimes"
        )

    # Simplify future assumptions by always making value a range
    if single_value:
        value = [value]

    if not _all_same_type(value):
        raise StreamlitAPIException(
            "Slider tuple/list components must be of the same type.\n"
            f"But were: {list(map(type, value))}"
        )

    if len(value) == 0:
        data_type = Slider.INT
    else:
        data_type = SUPPORTED_TYPES[type(value[0])]

    DEFAULTS = get_defaults(data_type, value)
    if min_value is None:
        min_value = DEFAULTS["min_value"]
    if max_value is None:
        max_value = DEFAULTS["max_value"]
    if step is None:
        step = DEFAULTS["step"]
        if data_type in (Slider.DATETIME, Slider.DATE) and (
            max_value - min_value < timedelta(days=1)
        ):
            step = timedelta(minutes=15)
    if format is None:
        format = DEFAULTS["format"]

    # Ensure that all arguments are of the same type.
    args = [min_value, max_value, step]
    int_args = all(map(lambda a: isinstance(a, int), args))
    float_args = all(map(lambda a: isinstance(a, float), args))
    # When min and max_value are the same timelike, step should be a timedelta
    timelike_args = (
        data_type in TIMELIKE_TYPES
        and isinstance(step, timedelta)
        and type(min_value) == type(max_value)
    )

    if not int_args and not float_args and not timelike_args:
        raise StreamlitAPIException(
            "Slider value arguments must be of matching types."
            "\n`min_value` has %(min_type)s type."
            "\n`max_value` has %(max_type)s type."
            "\n`step` has %(step)s type."
            % {
                "min_type": type(min_value).__name__,
                "max_type": type(max_value).__name__,
                "step": type(step).__name__,
            }
        )

    # Ensure that the value matches arguments' types.
    all_ints = data_type == Slider.INT and int_args
    all_floats = data_type == Slider.FLOAT and float_args
    all_timelikes = data_type in TIMELIKE_TYPES and timelike_args

    if not all_ints and not all_floats and not all_timelikes:
        raise StreamlitAPIException(
            "Both value and arguments must be of the same type."
            "\n`value` has %(value_type)s type."
            "\n`min_value` has %(min_type)s type."
            "\n`max_value` has %(max_type)s type."
            % {
                "value_type": type(value).__name__,
                "min_type": type(min_value).__name__,
                "max_type": type(max_value).__name__,
            }
        )

    # Ensure that min <= value <= max.
    if len(value) == 1:
        if not min_value <= value[0] <= max_value:
            raise StreamlitAPIException(
                "The default `value` of %(value)s "
                "must lie between the `min_value` of %(min)s "
                "and the `max_value` of %(max)s, inclusively."
                % {"value": value[0], "min": min_value, "max": max_value}
            )
    elif len(value) == 2:
        start, end = value
        if not min_value <= start <= end <= max_value:
            raise StreamlitAPIException(
                "The value and/or arguments are out of range. "
                "Expected: min_value <= start <= end <= max_value, "
                f"but was: {min_value} <= {start} <= {end} <= {max_value}"
            )
    else:
        value = [min_value, max_value]

    # Bounds checks. JSNumber produces human-readable exceptions that
    # we simply re-package as StreamlitAPIExceptions.
    # (We check `min_value` and `max_value` here; `value` and `step` are
    # already known to be in the [min_value, max_value] range.)
    try:
        if all_ints:
            JSNumber.validate_int_bounds(min_value, "`min_value`")
            JSNumber.validate_int_bounds(max_value, "`max_value`")
        elif all_floats:
            JSNumber.validate_float_bounds(min_value, "`min_value`")
            JSNumber.validate_float_bounds(max_value, "`max_value`")
        elif all_timelikes:
            # No validation yet. TODO: check between 0001-01-01 to 9999-12-31
            pass
    except JSNumberBoundsException as e:
        raise StreamlitAPIException(str(e))

    # Save the original timezone for conversion back to time/datetime (dates are always naive)
    orig_tz = value[0].tzinfo if data_type in (Slider.TIME, Slider.DATETIME) else None
    # Convert dates or times into datetimes
    if data_type == Slider.TIME:

        def _time_to_datetime(time):
            # Note, here we pick an arbitrary date well after Unix epoch.
            # This prevents pre-epoch timezone issues (https://bugs.python.org/issue36759)
            # We're dropping the date from datetime laters, anyways.
            return datetime.combine(date(2000, 1, 1), time)

        value = list(map(_time_to_datetime, value))
        min_value = _time_to_datetime(min_value)
        max_value = _time_to_datetime(max_value)

    if data_type == Slider.DATE:

        def _date_to_datetime(date):
            return datetime.combine(date, time())

        value = list(map(_date_to_datetime, value))
        min_value = _date_to_datetime(min_value)
        max_value = _date_to_datetime(max_value)

    # Now, convert to microseconds (so we can serialize datetime to a long)
    if data_type in TIMELIKE_TYPES:
        value = list(map(_datetime_to_micros, value))
        min_value = _datetime_to_micros(min_value)
        max_value = _datetime_to_micros(max_value)
        step = _delta_to_micros(step)

    # It would be great if we could guess the number of decimal places from
    # the `step` argument, but this would only be meaningful if step were a
    # decimal. As a possible improvement we could make this function accept
    # decimals and/or use some heuristics for floats.

    element.slider.label = label
    element.slider.format = format
    element.slider.default[:] = value
    element.slider.min = min_value
    element.slider.max = max_value
    element.slider.step = step
    element.slider.data_type = data_type

    return element, value, range_value, orig_tz


# TODO: always returning the same values
def fix_types(floats, data_type, orig_tz):
    if data_type == Slider.FLOAT:
        return floats
    if data_type == Slider.INT:
        return list(map(int, floats))
    if data_type == Slider.DATETIME:
        return [_micros_to_datetime(int(v), orig_tz) for v in floats]
    if data_type == Slider.DATE:
        return [_micros_to_datetime(int(v), orig_tz).date() for v in floats]
    if data_type == Slider.TIME:
        return [_micros_to_datetime(int(v), orig_tz).time() for v in floats]
