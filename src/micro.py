import speech_recognition as sr
import io

def isNumber(texto):
	try:
		_ = float(texto)
		return True
	except:
		return False

def preprocessamento(texto):
	texto = str(texto).strip().lower()
	texto = texto.split()
	for txt in texto:
		if isNumber(txt):
			return float(txt)

	return None

class Microfone:
	def __init__(self):
		self.microfone = sr.Recognizer()
		with sr.Microphone() as source:
			self.microfone.adjust_for_ambient_noise(source)

		self.source = sr.Microphone
		self.frames = None

	def gravar(self, source):
		if self.frames is None:
			self.frames = io.BytesIO()

		buffer = source.stream.read(source.CHUNK)

		if len(buffer) == 0: return False

		self.frames.write(buffer)
		return True

	def getText(self, source):
		if self.frames is None:
			raise Exception("É preciso gravar algum audio primeiro")

		frame_data = self.frames.getvalue()
		self.frames.close()
		self.frames = None

		audio = sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

		#with sr.Microphone() as source:
		#	audio = self.microfone.listen(source, timeout=0, phrase_time_limit=tempo)
		#	audio = self.microfone.record(source, duration=tempo)

		try:
			frase = self.microfone.recognize_google(audio, language='pt-BR')
			#print(frase)
			return frase
			#return preprocessamento(frase)
		except sr.UnknownValueError:
			return None

'''
def ouvir_microfone():
	microfone = sr.Recognizer()
	with sr.Microphone() as source:
		microfone.adjust_for_ambient_noise(source)

	#print("\x1b[2J\x1b[1;1H", end="")

	while True:
		input()
		with sr.Microphone() as source:
			audio = microfone.listen(source, phrase_time_limit=4)

		try:
			frase = microfone.recognize_google(audio,language='pt-BR')
			#print("Você disse: " + frase)
			#print("O que entendi: ")
			preprocessamento(frase)
		except sr.UnknownValueError:
			pass
			#print("Não entendi")

ouvir_microfone()
'''