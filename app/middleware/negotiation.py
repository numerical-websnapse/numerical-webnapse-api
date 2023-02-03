class NegotiationMiddleware:
    def process_request(self, req, resp):
        resp.content_type = req.accept