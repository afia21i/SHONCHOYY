from django import template

register = template.Library()

@register.filter
def times(number):
    try:
        number = int(number)
        return range(1, number + 1)
    except:
        return []

@register.filter
def divisible(value, arg):
    try:
        return round(float(value) / float(arg), 2)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
