from wsgiref.simple_server import make_server
import falcon, falcon_cors, pika, os

from app.controller.nsnp_controller import NSNP

from app.middleware.negotiation import NegotiationMiddleware

# amqp_url = os.environ['AMQP_URL']
# url_params = pika.URLParameters(amqp_url)
# connection = pika.BlockingConnection(url_params)

whitelisted_origins = [
    "http://localhost:4200",
    "https://<your-site>.com"
]

whitelisted_methods = [
    "GET",
    "PUT",
    "POST",
    "PATCH",
    "OPTIONS" # this is required for preflight request
]

cors = falcon_cors.CORS(
                                    allow_all_origins=True,
                                    # allow_origins_list=whitelisted_origins,
                                    # allow_origins_regex=None,
                                    allow_credentials_all_origins=True,
                                    # allow_credentials_origins_list=whitelisted_origins,
                                    # allow_credentials_origins_regex=None,
                                    allow_all_headers=True,
                                    # allow_headers_list=[],
                                    # allow_headers_regex=None,
                                    # expose_headers_list=[],
                                    allow_all_methods=True,
                                    # allow_methods_list=whitelisted_methods,
                                )

app = application = falcon.App( cors_enable=True,
                                middleware=[
                                    # cors.middleware,
                                    NegotiationMiddleware()
                                ]
                            )

# QUESTION ROUTES
app.add_route('/nsnp/simulate', NSNP(), suffix='simulate')

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()