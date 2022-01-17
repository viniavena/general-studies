import numpy as np
import cmath

#   algoritmo de solucao do sistema
#
#   ler a netlist
#       criar um dicionario para cada componente e add num array
#       pega a ordem sistema
#    cria uma matriz vazia Gn com a ordem do sistema e um vetor In com n linhas
#
#   ler o array de dicionarios
#       transformar o dicionario numa matriz com a estampa
#           somar essa matriz na matriz Gn
#           somar a corrente no vetor In
#
#   remover linhas e colunas do terra
#   solve com a matriz Gn e o vetor In


# funcao para leitura de netlist e conversao em matriz (split)
def readNetlist(arq):
    f = open(arq)
    lines = f.read().splitlines()
    f.close()

    netlist = []
    for component in lines:
        if component[0] != '*':
            netlist.append(component.split())

    return netlist

# funcao que dada uma netlist em matriz identifica a ordem do sistema


def sysOrder(netlist):
    order = 0
    for component in netlist:
        if int(component[1]) > order:
            order = int(component[1])
        if int(component[2]) > order:
            order = int(component[2])
    return order

# funcao que cria a matriz Gn


def createZeroMatriz(order):
    # return np.zeros([order,order], dtype=complex)
    matrix = []
    for i in range(order):
        matrix.append([0]*order)
    return matrix

# funcao que cria o vetor In


def createZeroArray(order):
    # return np.zeros(order)
    vector = []
    for i in range(order):
        vector.append(0)
    return vector

# funcao que cria um dicionario para cada componente


def createComponentObj(component):
    kind = component[0][0]
    if kind == 'R' or kind == 'L' or kind == 'C':
        item = {'id': component[0], 'nodeA': component[1],
                'nodeB': component[2], 'value': (component[3])}
    elif kind == 'K':
        item = {'id': component[0], 'nodeA': component[1], 'nodeB': component[2], 'inductance1': (component[3]),
                'nodeC': component[4], 'nodeD': component[5], 'inductance2': (component[6]), 'mutual': (component[7])}
    elif kind == 'I':
        if component[3].upper() == 'DC':
            item = {'id': component[0], 'nodeA': component[1],
                    'nodeB': component[2], 'type': component[3], 'value': (component[4])}
        else:
            item = {'id': component[0], 'nodeA': component[1], 'nodeB': component[2],
                    'type': component[3], 'amplitude': (component[4]), 'frequency': (component[5]), 'phase': (component[6])}
    elif kind == 'G':
        item = {'id': component[0], 'nodeA': component[1], 'nodeB': component[2], 'positiveV': component[3],
                'negativeV': component[4], 'value': (component[5])}
    return item

# funcao que dada a netlist cria uma lista de objetos de componentes


def listComponets(netlist):
    components = []
    for item in netlist:
        components.append(createComponentObj(item))
    return components


# estampas:

def createResistor(component, order):
    stamp = createZeroMatriz(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    value = float(component['value'])
    conductance = 1/value
    stamp[nodeA][nodeA] = stamp[nodeB][nodeB] = conductance
    stamp[nodeA][nodeB] = stamp[nodeB][nodeA] = conductance*(-1)
    return stamp


def createCapacitor(component, order, frequency):
    stamp = createZeroMatriz(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    value = float(component['value'])
    impedance = (value*1j*frequency)
    stamp[nodeA][nodeA] = stamp[nodeB][nodeB] = impedance
    stamp[nodeA][nodeB] = stamp[nodeB][nodeA] = impedance*(-1)
    return stamp


def createInductor(component, order, frequency):
    stamp = createZeroMatriz(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    value = float(component['value'])
    impedance = 1/(value*1j*frequency)
    stamp[nodeA][nodeA] = stamp[nodeB][nodeB] = impedance
    stamp[nodeA][nodeB] = stamp[nodeB][nodeA] = impedance*(-1)
    return stamp


def createControlledCurrent(component, order):
    stamp = createZeroMatriz(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    positiveV = int(component['positiveV'])
    negativeV = int(component['negativeV'])
    value = float(component['value'])
    stamp[nodeA][positiveV] = stamp[nodeB][negativeV] = value
    stamp[nodeA][negativeV] = stamp[nodeB][positiveV] = value*(-1)
    return stamp


def createTransformer(component, order, frequency):
    stamp = createZeroMatriz(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    nodeC = int(component['nodeC'])
    nodeD = int(component['nodeD'])
    inductance1 = float(component['inductance1'])
    inductance2 = float(component['inductance2'])
    mutual = float(component['mutual'])
    tau11 = inductance2/(inductance1*inductance2-mutual**2)
    tau22 = inductance1/(inductance1*inductance2-mutual**2)
    tau12 = -mutual/(inductance1*inductance2-mutual**2)
    stamp[nodeA][nodeA] = stamp[nodeB][nodeB] = tau11/(1j*frequency)  # tau11
    stamp[nodeA][nodeB] = stamp[nodeB][nodeA] = -tau11/(1j*frequency)  # -tau11
    stamp[nodeA][nodeC] = stamp[nodeB][nodeD] = stamp[nodeC][nodeA] = stamp[nodeD][nodeB] = tau12 / \
        (1j*frequency)  # tau12 e tau21
    stamp[nodeA][nodeD] = stamp[nodeB][nodeC] = stamp[nodeC][nodeB] = stamp[nodeD][nodeA] = - \
        tau12/(1j*frequency)  # -tau12 e -tau21
    stamp[nodeC][nodeC] = stamp[nodeD][nodeD] = tau22/(1j*frequency)  # tau22
    stamp[nodeC][nodeD] = stamp[nodeD][nodeC] = -tau22/(1j*frequency)  # -tau22
    return stamp


def createCurrentDC(component, order):
    stamp = createZeroArray(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    value = float(component['value'])
    stamp[nodeA] = value*(-1)
    stamp[nodeB] = value
    return stamp


def createSinCurrent(component, order):
    stamp = createZeroArray(order)
    nodeA = int(component['nodeA'])
    nodeB = int(component['nodeB'])
    amp = float(component['amplitude'])
    phase = float(component['phase'])
    current = amp * cmath.exp(1j * phase)
    stamp[nodeA] = current*(-1)
    stamp[nodeB] = current
    return stamp


# verifica qual o tipo de componente e retorna a estampa dele
def selectSimpleStamp(component, order, frequency):
    kind = component['id'][0]
    stamp = 0
    if kind == 'R':
        stamp = createResistor(component, order)
    elif kind == 'C':
        stamp = createCapacitor(component, order, frequency)
    elif kind == 'L':
        stamp = createInductor(component, order, frequency)
    elif kind == 'K':
        stamp = createTransformer(component, order, frequency)
    elif kind == 'G':
        stamp = createControlledCurrent(component, order)
    return stamp

# verifica qual o tipo de corrente e retorna a estampa dela


def selectCurrentStamp(component, order):
    stamp = 0
    if component['type'].upper() == 'DC':
        stamp = createCurrentDC(component, order)
    if component['type'].upper() == 'SIN':
        stamp = createSinCurrent(component, order)
    return stamp

# add uma estampa simples a matriz Gn


def addToGn(Gn, component, order, frequency):
    stamp = selectSimpleStamp(component, order, frequency)
    for i in range(len(Gn)):
        for j in range(len(Gn[0])):
            Gn[i][j] += stamp[i][j]

# add uma estampa de corrente ao vetor In


def addToIn(In, component, order):
    stamp = selectCurrentStamp(component, order)
    for i in range(len(In)):
        In[i] += stamp[i]

# percorre o array de componenentes e retorna a frequencia da fonte de corrente


def getFrequency(components):
    frequency = 0
    for element in components:
        if 'frequency' in element.keys():
            frequency = element['frequency']
    return float(frequency)

# percorre o array de componenets e add as estampas de cada as matrizes Gn e In


def addStamps(Gn, In, components, order, frequency):
    for component in components:
        kind = component['id'][0]
        if kind == 'I':
            addToIn(In, component, order)
        else:
            addToGn(Gn, component, order, frequency)

# dada uma matriz Gn e um vetor de correntes In, resolve o sistema:


def removeGroundLineAndColumn(Gn, In):
    In.pop(0)
    Gn.pop(0)
    for i in range(len(Gn)):
        Gn[i].pop(0)


def solveSystem(Gn, In):
    e = np.linalg.solve(Gn, In)
    return e


def finalPrint(Gn, In, e):
    print('\nMatriz Gn:')
    print(np.array(Gn))
    print('\nVetor In:')
    print(',\n'.join(map(str, In)))
    print('\nVetor E:')
    print(' V,\n'.join(map(str, e))+' V\n')


def initialPrint():
    print('\n'+20*"-")
    print("|    Trabalho CE2   |")
    print("|   Vinicius Avena  |")
    print(20*"-")
    print("\n")


def main():
    initialPrint()
    file = input('Entre com o aquivo de netlist: ')
    netlist = readNetlist(file)
    order = sysOrder(netlist) + 1  # add linha e coluna de zeros
    Gn = createZeroMatriz(order)
    In = createZeroArray(order)
    components = listComponets(netlist)
    frequency = getFrequency(components)
    addStamps(Gn, In, components, order, frequency)
    removeGroundLineAndColumn(Gn, In)
    e = solveSystem(Gn, In)
    finalPrint(Gn, In, e)


main()
