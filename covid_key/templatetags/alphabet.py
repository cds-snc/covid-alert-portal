from django.utils.translation import pgettext as _c
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
        return _c("phonetic", "A as in animal.")

    if letter == "E":
        return _c("phonetic", "E as in Elephant.")

    if letter == "F":
        return _c("phonetic", "F as in family.")

    if letter == "H":
        return _c("phonetic", "H as in hospital.")

    if letter == "J":
        return _c("phonetic", "J as in January.")

    if letter == "K":
        return _c("phonetic", "K as in kangaroo.")

    if letter == "L":
        return _c("phonetic", "L as in lion.")

    if letter == "Q":
        return _c("phonetic", "Q as in question.")

    if letter == "R":
        return _c("phonetic", "R as in radio.")

    if letter == "S":
        return _c("phonetic", "S as in september.")

    if letter == "U":
        return _c("phonetic", "U as in uniform.")

    if letter == "W":
        return _c("phonetic", "W as in Wi-Fi.")

    if letter == "X":
        return _c("phonetic", "X as in X-ray.")

    if letter == "Y":
        return _c("phonetic", "Y as in yoga.")

    if letter == "Z":
        return _c("phonetic", "Z as in zebra.")

    return ""
