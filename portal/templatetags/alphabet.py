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
        "B": _("B as in Banana."),
        "C": _("C as in Chocolate."),
        "D": _("D as in Doctor."),
        "E": _("E as in Espresso."),
        "F": _("F as in Family."),
        "G": _("G as in Garage."),
        "H": _("H as in Hospital."),
        "I": _("I as in Identity."),
        "J": _("J as in January."),
        "K": _("K as in Kangaroo."),
        "L": _("L as in Lion."),
        "M": _("M as in Music."),
        "N": _("N as in November."),
        "O": _("O as in October."),
        "P": _("P as in Planet."),
        "Q": _("Q as in Question."),
        "R": _("R as in Radio."),
        "S": _("S as in September."),
        "T": _("T as in Television."),
        "U": _("U as in Uniform."),
        "V": _("V as in Village."),
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
