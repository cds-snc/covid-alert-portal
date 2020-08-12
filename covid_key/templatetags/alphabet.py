from django.utils.translation import gettext as _
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


def _phonetic(letter):
    sentences = {
        "0": _("Zero."),
        "1": _("One."),
        "2": _("Two."),
        "3": _("Three."),
        "4": _("Four."),
        "5": _("Five."),
        "6": _("Six."),
        "7": _("Seven."),
        "8": _("Eight."),
        "9": _("Nine."),
        "A": _("A as in animal."),
        "E": _("E as in elephant."),
        "F": _("F as in family."),
        "H": _("H as in hospital."),
        "J": _("J as in January."),
        "K": _("K as in kangaroo."),
        "L": _("L as in lion."),
        "Q": _("Q as in question."),
        "R": _("R as in radio."),
        "S": _("S as in September."),
        "U": _("U as in uniform."),
        "W": _("W as in Wi-Fi."),
        "X": _("X as in X-ray."),
        "Y": _("Y as in yoga."),
        "Z": _("Z as in zebra."),
    }
    return sentences.get(letter, "")


@register.filter
@stringfilter
def phonetic(letter):
    letter = letter[0:1]
    if letter == "":
        return ""
    letter = letter.upper()
    return _phonetic(letter)
