import falcon

from app.model.NSNP import NumericalSNPSystem
from app.middleware.nsnp_validation import NSNPValidateMiddleware

class NSNP:
    @falcon.before(NSNPValidateMiddleware())
    def on_post_simulate(self, req, resp):
        if req.context.err:
            resp.media = {
                'resp' : 1,
                'message' : req.context.msg
            }; return
            
        data = req.media
        NSNP = NumericalSNPSystem(data['NSNP'])
        resp.media = NSNP.simulate(data['branch'],data['cur_depth'],data['sim_depth'])

    # ADD OTHER SIMULATION METHODS HERE