import matlab.engine
import argparse
import logging

log = logging.getLogger(__name__)

class matlab_client(object):
    def __init__(self, start_up = True):
        # Create the engine, but do not start it
        if(start_up):
            self.engine = self.start_engine()

    def start_engine(self):
        success = False
        try:
            self.engine = matlab.engine.start_matlab()
            log.info("matlab engine is generated")
            log.info("matlab engine is opened")
            success = True
        except Exception as e:
            print("Operation error: %s", e)

        return success

    def end_engine(self):
        if(self.engine != None):
            engine.close()

    def run(self, function_name, **args):
        param = dict()
        for key, value in args.items():
            print ("%s == %s" %(key, value))
            param[key] = value
        
        params = list(param.values())
        print("params:", params)
        print("self.engine", self.engine)
        func = getattr(self.engine, function_name)
        if(not params):
            func(nargout=0) 
        else:
            func(*params)

    def get_workspace_Data(self, field_name):
        data = eng.workspace[field_name]
        return data

    def set_workspace(self, field_name, value):
        eng.workspace[field_name] = value

    def numpy_examples(self):
        # with meg.Engine() as engine:
        data = numpy.empty((4,3))        
        # Copy Python data to the engine
        engine["data"] = data        
        # Execute MATLAB instructions
        engine("count = numel(data)")        
        # Get data from MATLAB
        print(engine["count"])

def example_of_func_without_params():
    client = matlab_client(start_up = True)
    client.start_engine()
    client.run(function_name="simpleplot")
    input("Press Enter to continue...")

def example_of_func_with_params():
    client = matlab_client(start_up = True)
    client.start_engine()
    client.run(function_name="simpleplot2", a=2, b=4)
    input("Press Enter to continue...")

def test():
    client = matlab_client(start_up = True)
    client.start_engine()
    client.run(function_name="Objective_function")
    #input("Press Enter to continue...")

def main():
    #example_of_func_without_params()
    #example_of_func_with_params()
    test()

if __name__ == "__main__":
    main()


