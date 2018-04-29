import itertools
import time
class Data_Match:
    def __init__(self,fragment_data,data):
        import itertools
        self.data = ['math.ceil(x)','math.floor(x)','math.fabs(x)','math.fmod(x,y)','math.frexp(x)','math.fsum(x)','math.gcd(x, y)','math.modf(x)','math.trunc(x)','math.exp(x)','math.log(x, y)','math.pow(x, y)','math.pow(x, y, z)','math.sqrt(x)','math.acos(x)','math.asin(x)','math.atan(x)','math.cos(x)','math.sin(x)','math.tan(x)','math.degrees(x)','math.radians(x)','statistics.mean(x)','statistics.harmonic_mean(x)','statistics.median(x)','statistics.median_low(x)','statistics.median_high(x)','statistics.median_grouped(x,y)','statistics.mode(x)','statistics.pstdev(x)','statistics.pvariance(x)','statistics.stdev(x)','statistics.variance(x)','abs(x)','divmod(x, y)','pow(x, y)','len(x)','min(x)','max(x)','x.count(y)','x.index(y)','del x[y:z]','x.append(y)','x.extend(y)','x *= y','x.insert(y, z)','x.remove(y)','x.reverse()','x.sort()','x.join()','str.capitalize(x)','sum(x)']
        if data != None:
            new_data =open(data,"r").read().split("\n\n")
            self.data+=new_data
        self.matches = []
        if fragment_data[0] == "console":
            self.console_check(fragment_data[1:])
        else:
            for fragment in fragment_data:
                self.check_fragment(fragment)
            self.unique_match()
        
    def unique_match(self):
        new_matches = []
        match_var = []
        for match in self.matches:
            if match[1] not in match_var:
                new_matches.append(match)
                match_var.append(match[1])
        self.matches = new_matches
    def console_check(self,datex):
        def check(code,input_list,output_val):
            import statistics
            import math
            outputlist = []
            input_variables = ["x","y","z"]
            output = None
            for i,input_value in enumerate(input_list):
                exec(input_variables[i]+" = "+input_value)
            if code[0] == "x":
                try:
                    output = eval(code)
                    if output == None:
                        output = eval("x")
                except:
                    return(False)
            else:
                try:
                    output = eval(code)
                except:
                    return(False)
            if str(output_val) == str(output):
#                input(output)
#                input(output_val)
                t2_start = time.perf_counter()
                output = eval(code)
                t2_stop = time.perf_counter()
                time_taken = t2_stop-t2_start
                return(time_taken)
            else:
                return(False)
        for code in self.data:
            inputlist = datex[0]
            output = datex[1]
            if check(code,inputlist,output) != False:
                self.matches.append(code)
                
            
    def check_fragment(self,fragment):
        def check_data(code,input_list,output_val):
            import statistics
            import math
            outputlist = []
            input_variables = ["x","y","z"]
            output = None
            for i,input_value in enumerate(input_list):
                exec(input_variables[i]+" = "+input_value)
            if code[0] == "x":
                try:
                    output = eval(code)
                    if output == None:
                        output = eval("x")
                except:
                    return(False)
            else:
                try:
                    output = eval(code)
                except:
                    return(False)
            if str(output_val) == str(output):
#                input(output)
#                input(output_val)
                t2_start = time.perf_counter()
                output = eval(code)
                t2_stop = time.perf_counter()
                time_taken = t2_stop-t2_start
                return(time_taken)
            else:
                return(False)
        
        for code in self.data:
#            print(fragment.output_val[0])
            try:
                result = check_data(code,fragment.input_val,fragment.output_val[0])
                if result != False:
                    self.matches.append([fragment,code,result])
                elif fragment.optional_input != []:
                    result = check_data(code,fragment.input_val+fragment.optional_input,fragment.output_val[0])
                    if result != False:
                        self.matches.append([fragment,code,result])
            except:
                continue