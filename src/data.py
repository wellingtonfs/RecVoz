import os

class Data:
    def __init__(self, pathRoot, data):
        self.currentModel = None
        self.pathSave = os.path.join(pathRoot, "data", "dados.csv")

        self.data = [self.init_data(v) for v in data]
        self.ponteiro = 0

    def init_data(self, d):
        d["modelo"] = {"valor": 'a', "tipo": "mod", "modelo": None} #modelo padrão
        self.currentModel = 'a'
        return d

    def setModel(self, model):
        self.currentModel = model

    def getModelKeys(self):
        return list(self.data[self.ponteiro]["__modelos"].keys())

    def getModels(self):
        return self.data[self.ponteiro]["__modelos"]

    def getOptions(self):
        return list(
            map(lambda x: ', '.join(
                [v for v in list(x.keys()) if not '__' in v and v != "modelo"]
            ), self.data)
        )

    def __str__(self):
        return ', '.join([v[1]['valor'] for v in self.getInfo() if v[0] != "modelo"])

    def getVars(self):
        if self.currentModel is None: return None

        return self.getFromModel(self.currentModel)

    def getInfo(self):
        return self.getFromModel(None)

    def getFromModel(self, model):
        lista = []
        if model in self.getModelKeys():
            for v in self.data[self.ponteiro]["__modelos"][model]:
                lista.append([v, self.data[self.ponteiro][v]])
            
        else:
            for v in list(self.data[self.ponteiro].items()):
                if '__' in v[0]:
                    continue

                if v[1]["modelo"] is None:
                    if model is None:
                        lista.append(v)

        return lista

    def updateVar(self, key, valor):
        self.data[self.ponteiro][key]["valor"] = str(valor)

    def getVarType(self, varname):
        return self.data[self.ponteiro][varname]["tipo"]

    def back(self):
        self.ponteiro -= 1
        if self.ponteiro < 0:
            self.ponteiro = len(self.data) - 1

    def next(self):
        self.ponteiro = (self.ponteiro + 1) % len(self.data)

    def saveData(self):
        mod = self.data[self.ponteiro]['modelo']['valor']

        titles = []
        dados = []

        for key in self.data[self.ponteiro]:
            d = self.data[self.ponteiro][key]

            if '__' in key or key == 'modelo': continue
            if d['modelo'] is not None and not mod in d['modelo']:
                d['valor'] = '0.0'

            titles.append(key)
            dados.append(d['valor'])

        if os.path.isfile(self.pathSave):
            titles = None

        with open(self.pathSave, 'a') as f:
            if titles is not None:
                f.write(','.join(titles) + '\n')
                
            f.write(','.join(dados) + '\n')

def GetDataFromTXT(pathRoot, path):
    with open(path, 'r') as f:
        texto = f.readlines()
        texto = [v.replace('\n', '') for v in texto if v[0] != '#' and len(v) > 1]

    partes = [{"__modelos": {}}]
    first_line = True
    count = 97
    for line in texto:
        l = [v.strip() for v in line.split(',')]

        if l[0] ==  "@@":
            partes.append({"__modelos": {}})
            first_line = True
            count = 97
            continue

        if first_line:
            count = 97
            for key in l:
                sepname = key.replace("__", "").strip().split('|')
                tipo = sepname[1] if len(sepname) > 1 else "txt"

                partes[-1][sepname[0]] = {"tipo": tipo, "valor": "0.0" if tipo == 'float' else "", "modelo": None}

            first_line = False
        else:
            for key in l:
                sepname = key.replace("__", "").strip().split('|')
                
                if partes[-1][sepname[0]]["modelo"] is None:
                    partes[-1][sepname[0]]["modelo"] = [chr(count)]
                else:
                    partes[-1][sepname[0]]["modelo"].append(chr(count))

            partes[-1]["__modelos"][chr(count)] = l

            count += 1

    return Data(pathRoot, partes)


if __name__ == "__main__":
    partes = GetDataFromTXT("/media/HD/Códigos/Sam/config.txt")
    print(partes.getModels())
    print("\n")
    print(partes.getInfo())
    print("\n")
    print(partes.getVars('a'))
    print("\n")
    print(partes.getVars('b'))
    print("\n")
    print(partes.updateVar("LT", "15.2"))
    print("\n")
    print(partes.getOptions())