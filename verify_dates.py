from datetime import date
from Transportation_APP.forms import get_bus_direction_dates

today = date.today()
day_name = today.strftime("%A")
print(f"Today: {today} ({day_name})\n")

print("Expected days of week:")
print("  Bus 1 Outbound: Tuesday")
print("  Bus 2 Outbound: Friday")
print("  Bus 1 Return: Wednesday")
print("  Bus 2 Return: Saturday\n")

print("Actual dates generated:\n")

for bus_num in [1, 2]:
    dep_date, ret_date = get_bus_direction_dates(bus_num, is_return_trip=False)
    dep_day = dep_date.strftime("%A")
    print(f"Bus {bus_num} OUTBOUND:")
    print(f"  Departure: {dep_date} ({dep_day})")
    print(f"  Return: {ret_date}")
    
    dep_date_ret, ret_date_ret = get_bus_direction_dates(bus_num, is_return_trip=True)
    dep_day_ret = dep_date_ret.strftime("%A")
    print(f"Bus {bus_num} RETURN:")
    print(f"  Departure: {dep_date_ret} ({dep_day_ret})")
    print(f"  Return: {ret_date_ret}")
    print()
