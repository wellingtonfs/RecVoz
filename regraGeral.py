
#Recebe uma key (nome da coluna no excel) e value (valor a ser salvo)
#Deve retornar uma string

def RegraDados(key, value) -> str:
    if 'obs' in key.lower() or value.isupper():
        return value

    return ' '.join([v.capitalize() for v in value.split()])