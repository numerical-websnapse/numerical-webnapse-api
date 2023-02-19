import falcon

from app.model.NSNP import NumericalSNPSystem
from app.middleware.nsnp_validation import NSNPValidateMiddleware



class NSNP:
    def error_handling(self, req, resp):
        if req.context.err:
            resp.media = {
                'resp' : 1,
                'message' : req.context.msg
            }; return True
        return False

    def response_handling(self, resp, resp_code, media):
        resp.media = {
            'resp' : resp_code,
            'message' : media
        }

    @falcon.before(NSNPValidateMiddleware())
    def on_post_simulate(self, req, resp):
        if self.error_handling(req, resp):
            return
            
        data = req.media
        NSNP = NumericalSNPSystem(data['NSNP'])

        self.response_handling(
            resp = resp,
            resp_code = 0,
            media = NSNP.simulate(data['branch'],data['cur_depth'],data['sim_depth'])
        )

    @falcon.before(NSNPValidateMiddleware())
    def on_post_simulate_single(self, req, resp):
        if self.error_handling(req, resp):
            return
            
        data = req.media
        NSNP = NumericalSNPSystem(data['NSNP'])
        
        self.response_handling(
            resp = resp,
            resp_code = 0,
            media = NSNP.simulate(data['branch'],data['cur_depth'],data['cur_depth']+1)
        )

    @falcon.before(NSNPValidateMiddleware())
    def on_post_spiking_matrix(self, req, resp):
        if self.error_handling(req, resp):
            return
            
        data = req.media
        NSNP = NumericalSNPSystem(data['NSNP'])

        self.response_handling(
            resp = resp,
            resp_code = 0,
            media = {
                'nrn_ord' : NSNP.neuron_keys,
                'fnc_ord' : NSNP.function_keys,
                'var_ord' : NSNP.variable_keys,
                'spike': NSNP.get_smatrix(config=NSNP.config_mx[0]).tolist(),
		    }
        )
    # ADD OTHER SIMULATION METHODS HERE