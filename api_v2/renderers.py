#Decimal places: 35.30 will be 35.30 and not 35.3

from rest_framework.renderers import JSONRenderer
from decimal import Decimal
import simplejson as json

class decimalJSONRenderer(JSONRenderer):
    encoder_class = json.JSONEncoder
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super(decimalJSONRenderer, self).render(data, accepted_media_type, renderer_context)

    