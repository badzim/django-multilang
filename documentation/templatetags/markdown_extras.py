import markdown as md
from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    # List of extensions to be used with the Markdown library
    extensions = [
        'codehilite',  # Syntax highlighting extension
        'fenced_code'  # Enables recognition of fenced code blocks
    ]
    # Debugging prints to understand what is received
    print("Original Value:", value)
    value = value.strip()
    after = mark_safe(md.markdown(value, extensions=extensions))
    print(after)
    return after
