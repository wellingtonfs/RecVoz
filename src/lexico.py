def isNumber(texto):
	try:
		_ = float(texto)
		return True
	except:
		return False

#retorna o valor significativo da msg
class Analise:
	def preprocess(self, texts):
		while texts.find(" ponto ") >= 0:
			texts = texts.replace(" ponto ", '.')

		return texts.lower().split()

	def __init__(self, texto, getText=False):
		texto = str(texto).strip().lower()
		
		self.value = None
		self.args = []
		self.ok = True
		self.isNumber = False
		self.cancelar = ["cancela", "cancelar", "errado", "errei", "não"]
		self.config = ["configurar", "configuração", "configurações"]
		self.change = ["altera", "alterar", "muda", "mudar", "trocar"]
		self.back = ["volta", "voltar", "vó", "vou"]
		self.voltar = ["volta", "voltar", "vó", "vou"]
		self.next = ["próximo", "avança", "avançar", "avance"]
		self.lok = ["ok", "feito", "terminei", "entrar"]
		self.original = texto

		texto = self.preprocess(texto)
		tsize = len(texto)

		if tsize == 0:
			self.ok = False
			return

		#comandos
		if texto[0] in self.change and 2 <= tsize <= 3:
			self.value = "change"
			self.args.append(texto[-1])
		elif tsize == 1 and texto[0] in self.back:
			self.value = "back"
		elif tsize == 1 and texto[0] in self.next:
			self.value = "next"
		elif tsize == 1 and texto[0] in self.lok:
			self.value = "ok"
		elif tsize == 1 and texto[0] in self.config:
			self.value = "config"
		elif getText:
			self.value = ' '.join(texto)
		else:
			self.ok = False

			for txt in texto[::-1]:
				if isNumber(txt):
					self.value = float(txt)
					self.isNumber = True
					self.ok = True