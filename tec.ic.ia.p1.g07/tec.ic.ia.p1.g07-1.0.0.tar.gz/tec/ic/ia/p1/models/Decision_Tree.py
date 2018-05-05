from tec.ic.ia.p1.models.Model import Model
from math import log
from numpy import argmax
import scipy.stats as stats

'''
Tree class.
Used for the creation of the decision tree.
'''


class DTree(object):
    def __init__(self):
        '''
        Constructor method.
        Initialize the variables.
        Parameters: None
        Return: None
        '''
        self.leaf_nodes = []
        self.nodes_conditions = []
        self.attribute = None


'''
DecisionTree class.
Creat the decision tree.
'''


class DecisionTree(Model):
    def __init__(self, samples_train, samples_test, prefix, pruning_threshold):
        super().__init__(samples_train, samples_test, prefix)
        '''
        Constructor method.
        Initialize the variables.
        Parameters:
            - samples_train: List with sublists. It must have the form [ [[attributes values], ... ,[attributes values]] , [outputs]]
            - samples_test:List with sublists. It must have the form [ [[attributes values], ... ,[attributes values]] , [outputs]]
            - prefix: String.
            - pruning_threshold: float. Between 0-1.
        Return: None
        '''
        self.votes = [['ACCESIBILIDAD SIN EXCLUSION',
                       'ACCION CIUDADANA',
                       'ALIANZA DEMOCRATA CRISTIANA',
                       'DE LOS TRABAJADORES',
                       'FRENTE AMPLIO',
                       'INTEGRACION NACIONAL',
                       'LIBERACION NACIONAL',
                       'MOVIMIENTO LIBERTARIO',
                       'NUEVA GENERACION',
                       'RENOVACION COSTARRICENSE',
                       'REPUBLICANO SOCIAL CRISTIANO',
                       'RESTAURACION NACIONAL',
                       'UNIDAD SOCIAL CRISTIANA',
                       'NULOS',
                       'BLANCOS'],
                      ['ACCION CIUDADANA',
                       'RESTAURACION NACIONAL',
                       'NULOS',
                       'BLANCOS']]
        self.pruning_threshold = pruning_threshold
        # Variables used in the gain function
        self.attribute_entropy = 0
        self.attributes_list = []  # Attribute Patrons: ["none", "some","full"]
        self.attributes_values = []  # Attribute Patrons: [5,4,8]
        self.outputs_list = []  # Outputs: ["PAC", "PRN"]
        self.outputs_values = []  # Outputs: [1454,845]
        self.total = []  # Outputs per attributes: [[800,700],[714,754],[963,125]]
        self.N = 0  # len(data)
        # Keep the values of all the attributes
        self.official_attributes = []
        self.values_official_attributes = []
        self.prediction = 0
        # Decision Tree
        self.main_tree = None
        self.official_outputs = []

    def gain(self, attribute, data):
        '''
        Calculate the gain of an attribute.
        Parameters:
            - Attribute: int value. Index of the attribute.
            - Data:  List of indexes of the rows of data in samples_train[k].
        Return: float. Gain result.
        '''
        self.N = len(data)
        self.take_out_information(attribute, data)
        self.general_entropy()
        final = (self.total_gain())
        if(attribute not in self.official_attributes):
            self.official_attributes += [attribute]
            self.values_official_attributes += [self.attributes_list]
        self.attribute_entropy = False
        self.attributes_list = []
        self.attributes_values = []
        self.outputs_values = []
        self.outputs_list = []
        self.total = []
        self.N = 0
        return (final)

    def take_out_information(self, attribute, data):
        '''
        Takes the values of the children of the attribute, the quantity for each one and the outputs.
        Is used in gain().
        Because it use the data set once, avoid going through it again to get the entropy of each attribute value.
        Parameters:
            - Attribute: int value. Index of the attribute.
            - Data:  List of indexes of the rows of data in samples_train[k].
        Return: None.
        '''
        for i in data:
            if (self.attributes_list.count(
                    self.samples_train[0][i][attribute]) == 0):
                self.attributes_list += [self.samples_train[0][i][attribute]]
                self.attributes_values += [1]
                lista_2 = []
                for j in self.outputs_list:
                    lista_2 += [0]
                self.total += [lista_2]
            else:
                self.attributes_values[self.attributes_list.index(
                    self.samples_train[0][i][attribute])] += 1
            if (self.outputs_list.count(self.samples_train[1][i]) == 0):
                self.outputs_list += [self.samples_train[1][i]]
                self.outputs_values += [1]
                for j in self.total:
                    j += [0]
            else:
                self.outputs_values[self.outputs_list.index(
                    self.samples_train[1][i])] += 1
            self.total[self.attributes_list.index(
                self.samples_train[0][i][attribute])][self.outputs_list.index(self.samples_train[1][i])] += 1

    def general_entropy(self):
        '''
        Calculates the entropy of the parent attribute with the values obtained in take_out_information.
        Is used in gain(). Stores the result in attribute_entropy.
        Parameters: None
        Return: None.
        '''
        for i in self.outputs_values:
            self.attribute_entropy += (i / self.N) * log((i / self.N), 2)
        self.attribute_entropy *= -1

    def total_gain(self):
        '''
        Calculates the gain of the parent attribute.
        Is used in gain().
        Parameters: None
        Return: float. Gain result.
        '''
        resultado = 0
        for i in range(len(self.attributes_values)):
            resultado_parcial = 0
            for j in range(len(self.outputs_values)):
                if(self.total[i][j] != 0):
                    resultado_parcial += (self.total[i][j] / self.attributes_values[i]) * log(
                        self.total[i][j] / self.attributes_values[i], 2)
            resultado += (self.attributes_values[i] /
                          self.N) * (-1) * (resultado_parcial)
        return(self.attribute_entropy - resultado)

    def generate_ranges(self):
        '''
        Converts the numerical values of a list to a String of the range where the number is found.
        Is used in execute(). Use the list samples_test and samples_train.
        Parameters: None
        Return: None.
        '''
        numbers_list = []
        for i in range(len(self.samples_train[0][0])):
            if(not isinstance(self.samples_train[0][0][i], type(""))):
                numbers_list += [i]
        if (numbers_list != []):
            for i in self.samples_train[0]:
                for j in numbers_list:
                    if(i[j] >= 0 and i[j] < 0.25):
                        i[j] = "[0 , 0.25["
                    elif(i[j] >= 0.25 and i[j] < 0.50):
                        i[j] = "[0.25 , 0.50["
                    elif(i[j] >= 0.50 and i[j] < 0.75):
                        i[j] = "[0.50 , 0.75["
                    elif(i[j] >= 0.75 and i[j] <= 1):
                        i[j] = "[0.75 , 1]"
            if(len(self.samples_test) > 0):
                for i in self.samples_test[0]:
                    for j in numbers_list:
                        if(i[j] >= 0 and i[j] < 0.25):
                            i[j] = "[0 , 0.25["
                        elif(i[j] >= 0.25 and i[j] < 0.50):
                            i[j] = "[0.25 , 0.50["
                        elif(i[j] >= 0.50 and i[j] < 0.75):
                            i[j] = "[0.50 , 0.75["
                        elif(i[j] >= 0.75 and i[j] <= 1):
                            i[j] = "[0.75 , 1]"

    def decision_tree_learning(self, examples, attributes, parent_examples):
        '''
        Main function that creates the decision tree. It uses most functions of the class.
        It works based on recursion.
        Parameters:
            - examples: int list. Contains the indexes of samples_train [0].
            - attributes: int list. Contains the indexes of samples_train [0][k] (attributes).
            - parent_examples: int list. Contains the indexes of samples_train [0] of the parent node.
        Return: DTree or String.
        '''
        # print("---------------------------------------------")
        if (examples == []):
            #print("Hoja: ",self.plurality_value(parent_examples))
            return self.plurality_value(parent_examples)
        elif (self.classification(examples)):
            #print("Hoja: ", self.samples_train[1][examples[0]])
            return self.samples_train[1][examples[0]]
        elif (attributes == []):
            #print("Hoja: ",self.plurality_value(examples))
            return self.plurality_value(examples)
        else:
            lista_r = [self.gain(i, examples) for i in attributes]
            # print(lista_r)
            tree = DTree()
            tree.attribute = attributes[argmax(lista_r)]
            ejemplos = [[] for i in range(
                len(self.values_official_attributes[tree.attribute]))]
            v = []
            for i in examples:
                v = self.values_official_attributes[self.official_attributes.index(
                    tree.attribute)]
                ejemplos[v.index(self.samples_train[0][i]
                                 [tree.attribute])] += [i]
            #print("Atributos :", v)
            #print("Atributos: ",attributes, "\nAtributo actual: ", tree.attribute)
            at = attributes[0:]  # con repetir atributos
            at.remove(tree.attribute)  # con repetir atributos
            # attributes.remove(tree.attribute) #sin repetir atributos
            for k in range(len(v)):
                tree.nodes_conditions += [v[k]]
                # con repetir atributos
                tree.leaf_nodes += [
                    self.decision_tree_learning(
                        ejemplos[k], at, examples)]
                # con repetir atributos
                #tree.leaf_nodes += [self.decision_tree_learning(ejemplos[k],attributes, examples)]
            return (tree)

    def classification(self, examples):
        '''
        Check if all the outputs of samples_train are equal.
        Is used in decision_tree_learning().
        Parameters:
            - examples: int list. Contains the indexes of samples_train [0].
        Return: boolean. True = equals.
        '''
        iguales = True
        valor = self.samples_train[1][examples[0]]
        for i in examples:
            if(self.samples_train[1][i] not in self.official_outputs):
                self.official_outputs += [self.samples_train[1][i]]
            if(self.samples_train[1][i] != valor):
                iguales = False
                break
        return iguales

    def plurality_value(self, examples):
        '''
        Returns the value of the outputs of samples_train that is in greater quantity.
        Is used in decision_tree_learning().
        Parameters:
            - examples: int list. Contains the indexes of samples_train [0].
        Return: string of the chosen output.
        '''
        outputs = []
        values = []
        for i in examples:
            if(self.samples_train[1][i] not in outputs):
                outputs += [self.samples_train[1][i]]
                values += [1]
            else:
                values[outputs.index(self.samples_train[1][i])] += 1
        return (outputs[argmax(values)])

    def pruning_tree(self, examples, tree):
        '''
        Main function that is responsible for pruning the tree according to the threshold.
        Is used in execute().
        Parameters:
            - examples: int list. Contains the indexes of samples_train [0].
            - tree: DTree.
        Return: Pruned DTree.
        '''
        attributes = []
        values = []
        for i in examples:
            if(self.samples_train[0][i][tree.attribute] not in attributes):
                attributes += [self.samples_train[0][i][tree.attribute]]
                values += [[i]]
            else:
                values[attributes.index(
                    self.samples_train[0][i][tree.attribute])] += [i]
        cant_hojas = 0
        for k in range(len(tree.leaf_nodes)):
            if (not isinstance(tree.leaf_nodes[k], type(""))):
                #atributo = tree.leaf_nodes[k].attribute
                tree.leaf_nodes[k] = self.pruning_tree(
                    values[attributes.index(tree.nodes_conditions[k])], tree.leaf_nodes[k])
                if (isinstance(tree.leaf_nodes[k], type(""))):
                    cant_hojas += 1
                    #print("Elimino atributo: ", atributo, " ahora es: ", tree.leaf_nodes[k])
            else:
                cant_hojas += 1
        if(cant_hojas > 0):
            desviation = self.total_deviation(attributes, values)
            if (desviation > self.pruning_threshold):
                #print(" + Desviacion: ", desviation, " para nodo: ", tree.attribute)
                return self.plurality_value(examples)
            else:
                return tree
        else:
            return tree

    def total_deviation(self, attributes, examples):
        '''
        Calculate the deviation of the node to evaluate if it is pruned or not.
        Use the chi square method. Is used in pruning_tree().
        Parameters:
            - attributes: list of attributes values. Example: ["some", "full"]
            - examples: List containing sublists with the indexes of samples_train[0].
                        The number of sublists corresponds to len(attributes).
        Return: float. Between 0-1, deviation result.
        '''
        outputs = []
        total_outputs = []
        total_examples = 0
        outputs_x_attributes = []
        result = 0
        for i in range(len(examples)):
            outputs_x_attributes += [[]]
            outputs_x_attributes[-1] = [0 for i in range((len(outputs)))]
            for j in examples[i]:
                if(self.samples_train[1][j] not in outputs):
                    outputs += [self.samples_train[1][j]]
                    total_outputs += [1]
                    total_examples += 1
                    outputs_x_attributes[i] += [1]
                else:
                    total_examples += 1
                    total_outputs[outputs.index(self.samples_train[1][j])] += 1
                    outputs_x_attributes[i][outputs.index(
                        self.samples_train[1][j])] += 1
        for i in range(len(outputs_x_attributes)):
            partial_result = 0
            for j in range(len(outputs_x_attributes[i])):
                true_irrelevance = total_outputs[j] * \
                    (len(examples[i]) / total_examples)
                partial_result += (
                    (outputs_x_attributes[i][j] - true_irrelevance)**2) / true_irrelevance
            result += partial_result
        return(1 - stats.chi2.cdf(x=result, df=((len(outputs) - 1) * (len(attributes) - 1))))

    def validate_data(self, data):
        '''
        Use the tree to classify the data, calculate the accuracy and return the classification obtained.
        Parameters:
            - data: samples_test or samples_train.
        Return: List of results. Convert the string output to int, according to the index of votes.
                Use votes[0] for r1 and votes[1] for r2 and r2_with_r1.
        '''
        count = 0
        partidos = []
        a_x_p = []
        result = []
        for i in range(len(data[0])):
            hijo = False
            arbol = self.main_tree
            while (hijo == False):
                if(arbol.nodes_conditions.count(data[0][i][arbol.attribute]) != 0):
                    arbol = arbol.leaf_nodes[arbol.nodes_conditions.index(
                        data[0][i][arbol.attribute])]
                    if(isinstance(arbol, type(""))):
                        hijo = True
                else:
                    print("Attribute: \"",
                          data[0][i][arbol.attribute],
                          "\" not found in tree.")
                    break
            #print("Era: ", data[1][i], " Salio: ", arbol)
            if (data[1][i] == arbol):
                result += [self.votes[self.prediction].index(data[1][i])]
                count += 1
                if(data[1][i] not in partidos):
                    partidos += [data[1][i]]
                    a_x_p += [[1, 1]]
                else:
                    a_x_p[partidos.index(data[1][i])][0] += 1
                    a_x_p[partidos.index(data[1][i])][1] += 1
            else:
                result += [self.votes[self.prediction].index(data[1][i])]
                if(data[1][i] not in partidos):
                    partidos += [data[1][i]]
                    a_x_p += [[1, 0]]
                else:
                    a_x_p[partidos.index(data[1][i])][0] += 1

        print("Success: ",
              count,
              " of: ",
              len(data[0]),
              " Accuracy: ",
              (count / len(data[0])))
        # for i in range(len(a_x_p)):
        #    print(partidos[i])
        #    print(a_x_p[i])
        return result

    def execute(self):
        '''
        Function that executes all the functions above.
        First get the indexes of samples_train[0] and the index of the attributes.
        Convert numeric attributes to string.
        Create the decision tree.
        Validate the tree data without pruning.
        Prune the tree according to the threshold.
        Validate the data with the pruned tree.
        Parameters: None
        Return: List of results according to the validation function.
        '''
        result = []
        self.official_attributes = []
        self.values_official_attributes = []
        self.main_tree = None
        self.official_outputs = []
        att = [i for i in range(len(self.samples_train[0][0]))]
        datos = [i for i in range(len(self.samples_train[0]))]
        self.generate_ranges()

        # The tree is created
        self.main_tree = self.decision_tree_learning(datos, att, datos)
        if(len(self.official_outputs) > 4):
            self.prediction = 0
        else:
            self.prediction = 1

        print("\n-------Before pruning--------")
        # The data is validated with a tree without pruning
        print("-> Training Set")
        self.validate_data(self.samples_train)
        print("-> Test Set")
        self.validate_data(self.samples_test)

        # The tree is pruned
        self.main_tree = self.pruning_tree(datos, self.main_tree)
        print("\n-------After pruning--------")
        if(isinstance(self.main_tree, type(""))):
            print("Tree ended as a single leaf: ", self.main_tree)
            print("-> Training Set")
            print(
                "Success: ", self.samples_train[1].count(
                    self.main_tree), " of: ", len(
                    self.samples_train[0]), " Accuracy: ", (self.samples_train[1].count(
                        self.main_tree) / len(
                        self.samples_train[0])))
            print("-> Test Set")
            print(
                "Success: ", self.samples_test[1].count(
                    self.main_tree), " of: ", len(
                    self.samples_test[0]), " Accuracy: ", (self.samples_test[1].count(
                        self.main_tree) / len(
                        self.samples_test[0])))
            return([self.votes[self.prediction].index(self.main_tree)] * ((len(self.samples_train[0]) + len(self.samples_test[0]))))
        else:
            # Validated data with pruned tree
            print("-> Training Set")
            result += self.validate_data(self.samples_train)
            print("-> Test Set")
            result += self.validate_data(self.samples_test)
            # print(result)
            print("\nEnding execution\n")
            return result
