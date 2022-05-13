import os
from datetime import datetime
import pandas as pd

def getDate():
    date = datetime.now()

    return ('%2d_%2d_%d' %(date.day, date.month, date.year)).replace(' ', '0')

class Data:
    def __init__(self, pathRoot, data, funcR):
        self.currentModel = None
        self.pathSave = {}

        self.dicionario = data["dicionario"]
        self.comandos = data["comandos"]
        self.dadosGerais = data["vars"]

        self.optGeral = list(self.dadosGerais.keys())

        self.modeloAtual = 0
        self.posOptGeral = 0

        self.pathRoot = pathRoot
        self.funcR = funcR

        for name in data["vars"]:
            self.pathSave[name] = os.path.join(pathRoot, "data", "%s_%s.xlsx" %(name, getDate()))
            self.pathSave[name+'bkp'] = os.path.join(pathRoot, "data", "%s_%s_bkp.txt" %(name, getDate()))

            if os.path.isfile(self.pathSave[name]):
                tab = pd.read_excel(self.pathSave[name], index_col=0).fillna('').astype(str)
                self.setTab(name, tab)

    def getOptName(self):
        return self.optGeral[self.posOptGeral]

    def getTab(self, name):
        return self.dadosGerais[name]["tabela"]

    def getLastLines(self, qtd):
        tab = self.getTab(self.getOptName())

        idx = tab.last_valid_index()
        if idx is None: return ["Sem Dados" for _ in range(qtd)]

        ini = max(0, idx - (qtd - 1))

        dados = []
        for line in tab.loc[ini:idx].values:
            dados.insert(0, ', '.join(line))

        while len(dados) < qtd:
            dados.append("Sem Dados")

        return dados

    def setTab(self, name, tab):
        self.dadosGerais[name]["tabela"] = tab.fillna('')

    def getModels(self, current=False):
        if current:
            return self.dadosGerais[self.getOptName()]["modelos"]

        modelos = {}

        for name in self.dadosGerais:
            modelos[name] = self.dadosGerais[name]["modelos"]

        return modelos

    def getStaticVars(self):
        dados = self.dadosGerais[self.getOptName()]["dados"]

        return list(filter(lambda x: x[1]["modelo"] is None, dados.items()))

    def getDinamicVars(self):
        dados = self.dadosGerais[self.getOptName()]["dados"]
        modelo = self.dadosGerais[self.getOptName()]["modelos"][self.modeloAtual]

        return [
            (mod, dados[mod]) for mod in modelo
        ]

    def updateVar(self, key, value):
        key, value = str(key), str(value)

        for name in self.dicionario:
            if key.lower() == name.lower():
                for fromStr, toStr in self.dicionario[name].items():
                    value = value.replace(fromStr, toStr)

        for name in self.comandos:
            if key.lower() == name.lower():
                for cmd in self.comandos[name]:
                    value = cmd(key, value)

        value = self.funcR(key, str(value))

        self.dadosGerais[self.getOptName()]["dados"][key]["valor"] = value

    def dropLast(self):
        name = self.getOptName()
        tab = self.getTab(name)

        idx = tab.last_valid_index()
        if idx is None: return

        tab = tab.drop(index=idx)

        self.setTab(name, tab)

    def save(self):
        dados = self.dadosGerais[self.getOptName()]["dados"]
        titulo, vars = [], []
    
        for name in dados:
            valor = dados[name]["valor"]

            if dados[name]["modelo"] and not self.modeloAtual in dados[name]["modelo"]:
                valor = '0.0'

            titulo.append(name)
            vars.append(valor)

        with open(self.pathSave[self.getOptName()+'bkp'], 'a') as f:
            line = ','.join(vars)
            line = self.getOptName() + ': ' + line + '\n'
            f.write(line)

        serie = pd.DataFrame([vars], columns=titulo)

        tab = self.getTab(self.getOptName())
        tab = pd.concat([tab, serie], ignore_index=True)
        self.setTab(self.getOptName(), tab)

        tab.to_excel(self.pathSave[self.getOptName()])

def mostrardados(dado, c=0):
    if type(dado) == dict:
        for k in dado:
            print(' '*c, k)
            aux = c
            c += 5
            mostrardados(dado[k], c)
            c = aux
    elif type(dado) == list:
        print(' '*c, dado)
    else:
        print(' '*c, dado)

def GetDataFromTXT(pathRoot, path, funcR):
    with open(path, 'r') as f:
        texto = f.readlines()
        texto = [v.replace('\n', '') for v in texto if v[0] != '#' and len(v) > 1]

    #[print(t) for t in texto]
    #print(" ")

    first_line = True
    count = 0

    dados = {
        "dicionario": {},
        "comandos": {},
        "vars": {}
    }
    partDict = None

    for line in texto:
        line = [v.strip() for v in line.split(',')]

        if line[0] ==  "@@":
            first_line = True
            count = 0
            continue

        if line[0][0] == '&':
            partDict = line[0][1:]
            continue
        
        if partDict is not None:
            if line[0][0] != '$':
                line = line[0].strip().split('->')
                words = [None, None]

                for i, w in enumerate(line):
                    for letra in w:
                        if letra == "'":
                            if words[i]:
                                break
                            else:
                                words[i] = []

                        elif words[i] is not None:
                            words[i].append(letra)

                if partDict in dados["dicionario"].keys():
                    dados["dicionario"][partDict][''.join(words[0])] = ''.join(words[1])
                else:
                    dados["dicionario"][partDict] = { ''.join(words[0]) : ''.join(words[1]) }
            else:
                line = ','.join(line)
                cmd = line[1:]

                try:
                    if partDict in dados["comandos"].keys():
                        dados["comandos"][partDict].append( eval(cmd) )
                    else:
                        dados["comandos"][partDict] = [ eval(cmd) ]
                except:
                    print("Alguma função criada no arquivo config.txt (inicio: $) está mal formulada:\n\t%s" %cmd)
                    exit(1)

        elif first_line:
            name, var1 = line[0].split(':')
            line[0] = var1
            dados["vars"][name] = {
                "dados": {},
                "modelos": {},
                "tabela": pd.DataFrame()
            }
            count = 0

            for var in line:
                sepname = var.replace("_", "").strip().split('|')
                tipo = sepname[1] if len(sepname) > 1 else "txt"

                dados["vars"][name]["dados"][sepname[0]] = {
                    "tipo": tipo,
                    "valor": "0.0" if tipo == 'float' else "",
                    "modelo": None
                }

            first_line = False
        else:
            for var in line:
                sepname = var.replace("_", "").strip().split('|')

                if dados["vars"][name]["dados"][sepname[0]]["modelo"] is None:
                    dados["vars"][name]["dados"][sepname[0]]["modelo"] = [count]
                else:
                    dados["vars"][name]["dados"][sepname[0]]["modelo"].append(count)

            if dados["vars"][name]["modelos"]:
                dados["vars"][name]["modelos"].append(line)
            else:
                dados["vars"][name]["modelos"] = [line]

            count += 1

    #mostrardados(dados["comandos"])
    #mostrardados(dados)

    return Data(pathRoot, dados, funcR)


if __name__ == "__main__":
    partes = GetDataFromTXT("/home/wellington/Documentos/RecVoz", "/home/wellington/Documentos/RecVoz/config.txt")
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