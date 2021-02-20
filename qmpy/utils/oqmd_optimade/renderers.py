from rest_framework.negotiation import DefaultContentNegotiation

class IgnoreClientContentNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        # Allow URL style format override.  eg. "?format=json
        format_query_param = self.settings.URL_FORMAT_OVERRIDE
        format = format_suffix or request.query_params.get(format_query_param)
        if format is None:
            return (renderers[0], renderers[0].media_type)
        else:
            return DefaultContentNegotiation.select_renderer(self, request, renderers, format_suffix)

