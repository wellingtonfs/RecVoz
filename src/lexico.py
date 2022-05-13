#retorna o valor significativo da msg
cAcento = ['á', 'à', 'â', 'ã', 'é', 'ê', 'í', 'ó', 'õ', 'ô', 'ú', 'ç']
sAcento = ['a', 'a', 'a', 'a', 'e', 'e', 'i', 'o', 'o', 'o', 'u', 'c']
numsExt = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
numsExtF = ["zero", "uma", "duas"]
meses = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

class Analise:
	def preprocess(self, texts):
		global cAcento, sAcento, numsExt, numsExtF

		texts = "" if texts is None else texts

		texts = str(texts).strip().lower()
		texts = texts.replace(" ponto ", '.').split()

		for i in range(len(texts)):
			if texts[i] in numsExt:
				texts[i] = "%.1f" %(float(numsExt.index(texts[i])))
			elif texts[i] in numsExtF:
				texts[i] = "%.1f" %(float(numsExtF.index(texts[i])))

		texts = ' '.join(texts)
		
		ltext = list(texts)
		for i in range(len(ltext)):
			if ltext[i] in cAcento:
				ltext[i] = sAcento[cAcento.index(ltext[i])]

		return ''.join(ltext)

	def __init__(self, texto):
		texto = self.preprocess(texto)

		self.cmd = []
		self.number = ""
		self.text = texto
		self.ok = True

		texto = texto.split()

		cancelar = ["cancela", "cancelar"]
		self.config = ["configurar", "configuracao", "configuracoes"]
		change = ["altera", "alterar", "muda", "mudar", "trocar"]
		back = ["volta", "voltar", "vo", "vou", "volto"]
		next = ["proximo", "avanca", "avancar", "avance"]
		ok = ["ok"]

		tsize = len(texto)

		if tsize == 0:
			self.text = "Não entendi"
			self.ok = False
			return

		#comandos
		for palavra in texto:
			if palavra in cancelar:
				self.text = "Cancelado!"
				self.ok = False
				break
			elif palavra in self.config:
				self.cmd.append("config")
			elif palavra in change:
				self.cmd.append("change")
				self.cmd.append(texto[-1])
			elif palavra in back:
				self.cmd.append("back")
			elif palavra in next:
				self.cmd.append("next")
			elif palavra in ok:
				self.cmd.append("ok")
			
			if self.isNumber(palavra):
				self.number = palavra if '.' in palavra else palavra + '.0'

	def isNumber(self, texto):
		try:
			_ = float(texto)
			return True
		except:
			return False

	def convertDate(self, texto):
		global meses

		texto = texto.split()
		texto = [
			str(meses.index(t) + 1) if t in meses else str(t) for t in texto
		]

		nums = []

		for t in texto:
			if self.isNumber(t):
				tn = t.split('.')[0]
				nums.append(tn if len(tn) > 1 else '0' + tn)

		if len(nums) == 3:
			return '/'.join(nums)

		return None

	def getInt(self):
		if not self.number:
			None
		
		return int(float(self.number))