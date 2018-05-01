from matplotlib import pyplot as plt
import itertools, json, os

OS = os.name
USER_HOME = os.environ.get('Homepath' if OS == 'nt' else 'HOME')
USER_DOC_PATH = USER_HOME + '\\Documents\\' if OS == 'nt' else USER_HOME + '/Documents/'

def sumlist(x):
    """
    sumlist(x)

    Returns the running sum of a list of numbers, x. For example:
    sumlist([1,2,3]) would return [1,3,6].
    """
    try:
        return list(itertools.accumulate(x))
    except TypeError:
        raise TypeError("unsupported argument type for 'sumlist'")

class AnalysisError(Exception):
    pass

class E80Analysis:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__),'e80data.json'), 'r') as f:
            self.e80data = json.load(f)
            self.spans = range(10,201)
    
    def set_spans(self, span_lengths):
        self.spans = span_lengths
        
    def _run_train_single_span(self, span_length, axles):
        incr = 1

        axle_loads = axles[0]
        axle_spaces = axles[1]
        axle_locs = sumlist(axle_spaces)

        train_tot = sum(axle_spaces)

        positions = []
        point = -span_length
        while point <= train_tot:
            positions.append(point)
            point += incr
        m_array = []
        v_array = []
        for i in range(len(positions)):
            x_locs_total = [-x + positions[i] + span_length for x in axle_locs]
            x_locs = [x for x in x_locs_total if (x <= span_length and x >= 0)]
            axles_ = [axle for axle in axle_locs if axle <= span_length + positions[i] and axle >= positions[i]]
            axle_loads_ = [axle_loads[k] for k, axle in enumerate(axle_locs) if axle in axles_]
            num_axles_ = len(axles_)
            # a and b arrays store a and b values or each axle
            # r1 and r2 arrays store reactions at ends 1 and 2 for each axle
            # m and v arrays store m and v caused by each axle
            r1 = []
            r2 = []
            m = []
            v = []

            # This loop calculates individual values for each of the above
            # arrays and appends each value to the array.
            for j in range(num_axles_):
                a_val = span_length + positions[i] - axles_[j]

                b_val = span_length - a_val

                if 0 < b_val < span_length:
                    r1_val = axle_loads_[j]*b_val/span_length
                else:
                    r1_val = 0
                r1.append(r1_val)

                if 0 < a_val < span_length:
                    r2_val = axle_loads_[j]*a_val/span_length
                else:
                    r2_val = 0
                r2.append(r2_val)

                m_loc = []
                v_loc = []
                for x_loc in x_locs:
                    if 0 < b_val < span_length and a_val > x_loc:
                        m_val = axle_loads_[j]*(a_val - x_loc)
                    else:
                        m_val = 0
                    m_loc.append(m_val)

                    if 0 < b_val < span_length and a_val < x_loc:
                        v_val = axle_loads_[j]
                    else:
                        v_val = 0
                    v_loc.append(v_val)
                m.append(m_loc if m_loc != [] else [0])
                v.append(v_loc if v_loc != [] else [0])
            # Calculate the moment and shear at the respective x location
            # caused by the train at position i and push these values to the
            # global moment and shear arrays
            moments = list(zip(*m))
            if x_locs != []:
                m_tot = max([sum(r2)*(span_length-x_locs[i]) - sum(moments[i]) for i in range(len(x_locs))])
            else:
                m_tot = 0
            v_tot = max(sum(r1), sum(r2))
            m_array.append(m_tot)
            v_array.append(v_tot)
        return max(m_array), max(v_array)
    
    def _get_single_E80_env(self, span):
        if str(span) in self.e80data.keys():
            return self.e80data[str(span)]
        else:
            axles_E80 = ([40,80,80,80,80,52,52,52,52]*2 + [8]*span, [0,8,5,5,5,9,5,6,5,8,8,5,5,5,9,5,6,5,5.5]+[1]*(span-1))
            axles_E80_alt = ([100,100,100,100], [0,5,6,5])
            e80_vals = self._run_train_single_span(span, axles_E80)
            e80_alt_vals = self._run_train_single_span(span, axles_E80_alt)
            return (max([e80_vals[0], e80_alt_vals[0]]), max([e80_vals[1], e80_alt_vals[1]]))
    
    def _calc_e80(self, design, e80):
        return (design[0]/e80[0] * 80, design[1]/e80[1] * 80)
    
    def span(self, axles, span):
        return self._calc_e80(self._run_train_single_span(span, axles), self._get_single_E80_env(span))
    
    def plot(self, axles, save=False):
        
        span_data = [self.span(axles, span) for span in self.spans]
        plt.plot(self.spans, [x[0] for x in span_data], label='Moment')
        plt.plot(self.spans, [x[1] for x in span_data], label='Shear')
        plt.legend()
        plt.minorticks_on()
        plt.grid()
        plt.title("Equivalent E-Loadings")
        plt.xlabel('Span Length, ft')
        plt.ylabel('E-Rating')
        if save:
            plt.savefig(USER_DOC_PATH+'E-Loading.png')
        else:
            plt.show()
        plt.clf()
        plt.cla()
        plt.close()