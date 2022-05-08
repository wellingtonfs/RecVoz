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

microfone = sr.Recognizer()
with sr.Microphone() as source:
    microfone.adjust_for_ambient_noise(source)

#print("\x1b[2J\x1b[1;1H", end="")

while True:
    with sr.Microphone() as source:
        frames = io.BytesIO()

        #--
        buffer = source.stream.read(source.CHUNK)
        #if len(buffer) == 0: break

        frames.write(buffer)
        #--

        frame_data = frames.getvalue()
        frames.close()

        audio = sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

        audio = microfone.listen(source)

    try:
        frase = microfone.recognize_google(audio,language='pt-BR')
        #print("Você disse: " + frase)
        #print("O que entendi: ")
        print(frase)
        #preprocessamento(frase)
    except sr.UnknownValueError:
        pass
        #print("Não entendi")