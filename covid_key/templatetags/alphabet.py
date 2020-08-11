from django.utils.translation import gettext as _
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def phonetic(letter):
    letter = letter[0:1]
    if letter == "":
        return ""
    letter = letter.upper()

    if letter == "0":
        return _("Zero.")

    if letter == "1":
        return _("One.")

    if letter == "2":
        return _("Two.")

    if letter == "3":
        return _("Three.")

    if letter == "4":
        return _("Four.")

    if letter == "5":
        return _("Five.")

    if letter == "6":
        return _("Six.")

    if letter == "7":
        return _("Seven.")

    if letter == "8":
        return _("Eighth.")

    if letter == "9":
        return _("Nine.")

    if letter == "A":
        return _("A as in animal.")

    if letter == "E":
        return _("E as in elephant.")

    if letter == "F":
        return _("F as in family.")

    if letter == "H":
        return _("H as in hospital.")

    if letter == "J":
        return _("J as in January.")

    if letter == "K":
        return _("K as in kangaroo.")

    if letter == "L":
        return _("L as in lion.")

    if letter == "Q":
        return _("Q as in question.")

    if letter == "R":
        return _("R as in radio.")

    if letter == "S":
        return _("S as in September.")

    if letter == "U":
        return _("U as in uniform.")

    if letter == "W":
        return _("W as in Wi-Fi.")

    if letter == "X":
        return _("X as in X-ray.")

    if letter == "Y":
        return _("Y as in yoga.")

    if letter == "Z":
        return _("Z as in zebra.")

    return ""
