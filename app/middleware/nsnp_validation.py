from marshmallow import fields, Schema, ValidationError, validate, validates_schema, INCLUDE, EXCLUDE
import falcon, json

NSNP_tags = ['neurons','syn','in','out']

class FunctionSchema(Schema):
    class Meta:
        unknown = INCLUDE

    thld = fields.Float(required=True, allow_none=True)

    @validates_schema
    def validate_availability(self, data, **kwargs):
        for dt in data:
            if dt not in ['thld']:
                if type(data[dt]) not in [int,float]:
                    raise ValidationError("Invalid data type for function parameter", field_name=dt)

class NeuronSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    var = fields.Dict(
        required=True,
        keys=fields.String(required=True),
        values=fields.Float(required=True)
    )

    prf = fields.Dict(
        required=True, 
        keys=fields.String(required=True),
        values=fields.Nested(FunctionSchema)
    )

class NSNPSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    neurons = fields.Dict(
        required=True,
        keys=fields.String(required=True),
        values=fields.Nested(NeuronSchema)
    )
    syn = fields.List(fields.List(fields.String),required=True)
    in_ = fields.List(fields.String(),required=True)
    out = fields.List(fields.String(),required=True)

class SimulationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    NSNP = fields.Nested(NSNPSchema)
    branch = fields.Int(required=True,allow_none=True)
    cur_depth = fields.Int(required=True)
    sim_depth = fields.Int(required=True)

    @validates_schema
    def validate_availability(self, data, **kwargs):
        if data['cur_depth'] > data['cur_depth']:
            raise ValidationError("Current depth is greater than simulation depth", field_name="cur_depth")

    def branch_validation(self, data, **kwargs):
        if data['branch'] is not None:
            if data['branch'] < 1:
                raise ValidationError("Invalid branch size (branch > 1)", field_name="branch")

class NSNPValidateMiddleware(object):
    def __init__(self):
        pass

    def __call__(self, req, resp, resource, params):
        req.context.err, req.context.msg = \
            self.validate(SimulationSchema(unknown=EXCLUDE),req.media)

    def validate(self,schema,data):
        try: schema.load(data);\
            return False, 'Validated'
        except ValidationError as err:
            return True, err.messages_dict

if __name__ == "__main__":
    schema = SimulationSchema()
    try:
        result = schema.load({
        "NSNP": {
            "neurons": {
                "n_1": {
                    "var": {
                        "x_{1,1}": 1,
                        "x_{2,1}": 1
                    },
                    "prf": {
                        "f_{1,1}": {
                            "thld": 1,
                            "x_{1,1}": 0.5,
                            "x_{2,1}": 0.5
                        }
                    }
                },
                "n_2": {
                    "var": {
                        "x_{1,2}": 1
                    },
                    "prf": {
                        "f_{1,2}": {
                            "thld": None,
                            "x_{1,2}": 1
                        },
                        "f_{2,2}": {
                            "thld": None,
                            "x_{1,2}": -1
                        }
                    }
                },
                "n_3": {
                    "var": {
                        "x_{1,3}": 0
                    },
                    "prf": {
                        "f_{1,3}": {
                            "thld": None,
                            "x_{1,3}": 1
                        }
                    }
                },
                "n_4": {
                    "var": {
                        "x_{1,4}": 0
                    },
                    "prf": {
                        "f_{1,4}": {
                            "thld": None,
                            "x_{1,4}": -1
                        }
                    }
                },
                "n_5": {
                    "var": {
                        "x_{1,5}": 2
                    },
                    "prf": {
                        "f_{1,5}": {
                            "thld": None,
                            "x_{1,5}": 0.5
                        }
                    }
                }
            },
            "syn": [
                ["n_1", "n_2"],
                ["n_2", "n_1"],
                ["n_1", "n_3"],
                ["n_2", "n_4"],
                ["n_3", "n_5"],
                ["n_4", "n_5"]
            ],
            "in_": [],
            "out": ["n_5"]
        },
        "branch": None,
        "cur_depth": 0,
        "sim_depth": 100
    })
        print(result)
    except ValidationError as err:
        print(err.messages_dict)