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
        "A": _("A as in Animal."),
        "E": _("E as in Espresso."),
        "F": _("F as in Family."),
        "H": _("H as in Hospital."),
        "J": _("J as in January."),
        "K": _("K as in Kilo."),
        "L": _("L as in Lion."),
        "Q": _("Q as in Question."),
        "R": _("R as in Radio."),
        "S": _("S as in September."),
        "U": _("U as in Uniform."),
        "W": _("W as in Wi-Fi."),
        "X": _("X as in X-ray."),
        "Y": _("Y as in Yoga."),
        "Z": _("Z as in Zebra."),
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
