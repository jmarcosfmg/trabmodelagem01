import numpy as np
import random
from datetime import datetime as dt
import threading
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

relogio = 0.0
relogio_hc = 0.0
relogio_hs = 0.0
ultima_chegada = 0.0
tec_det = False
ts_det = False
num_cliente = 0
servidor_em_atendimento = False
tam_max_fila = float('inf')
arr_entradas = []
arr_fila = []
arr_prob_tec = []
arr_prob_ts = []
buffer_csv = []
nome_arquivo = ""
cliente_em_atendimento = []

arr_tempos_espera = []
arr_tempos_espera_mean = []
arr_tempos_atendimento = []
arr_tempos_atendimento_mean = []
arr_tempos_chegada = []
arr_tempos_chegada_mean = []
arr_tamanhos_fila = []
arr_tamanhos_fila_mean = []

def mostra_menu(estado = None):
	global tec_det, ts_det, tam_max_fila
	print("\n\nMenu:")
	while True:
		print("O Tempo entre chegadas (TEC) é determinístico? [S/N]")
		x = input().upper()
		if (x == "S" or x == "N"):
			tec_det = True if x == "S" else False
			break
	while True:
		print("O Tempo de serviço (TS) é determinístico? [S/N]")
		x = input().upper()
		if (x == "S" or x == "N"):
			ts_det = True if x == "S" else False
			break
	while True:
		print("A fila tem limite? [S/N]")
		x = input().upper()
		if (x == "S"):
			while True:
				print("Qual é o limite da fila?")
				try:
					tam_max_fila = int(input())
					if(tam_max_fila < 0):
						raise TypeError("Insira um número >= 0.")
					break
				except:
					erro("Insira um número >= 0.")
		if (x == "N" or x == "S"):
			break
	print("")

def ler_entradas():
	global arr_entradas
	print("Para cada novo evento, informe os dados", end="")
	if (not(tec_det or ts_det)): 
		print(" da seguinte forma: TEC [ESPAÇO] TS", end="")
	elif (not tec_det):
		print(" TEC", end="")
	elif (not ts_det):
		print(" TS", end="")
	print(", seguidos pela tecla ENTER.")
	print("Para finalizar a inserção dos dados, digite 'done' e aperte ENTER")
	valor_informado = input()
	while(valor_informado.strip().upper() != "DONE"):
		valor_informado = valor_informado.strip()
		if (not(tec_det or ts_det)): 
			try:
				tec_, ts_ = valor_informado.split(' ')
				tec_ = float(tec_.strip())
				ts_ = float(ts_.strip())
				if(tec_ <= 0 or ts_ <= 0):
					raise TypeError() 
				arr_entradas.append((tec_,ts_))
			except:
				warning("Os tempos entre chegadas e o tempo de serviço devem ser valores numéricos > 0.")
		elif(not tec_det):
			try:
				tec_ = float(valor_informado)
				if(tec_ <= 0):
					raise TypeError() 
				arr_entradas.append(tec_)
			except:
				warning("O tempo entre chegadas deve ser um valor numérico > 0.")
				continue
		else:
			try:
				ts_ = float(valor_informado)
				if(ts_ <= 0):
					raise TypeError() 
				arr_entradas.append(ts_)
			except:
				warning("O tempo de serviço deve ser um valor numérico > 0.")
		valor_informado = input()

def ler_det():
	global arr_prob_tec, arr_prob_ts
	warning("Os valores devem preenchidos usando o tempo.\nPor exemplo: Se 15 carros chegam por hora, o TEC deve ser 4 (se o tempo for contado em minutos) ou 0.06 (se for contado em horas)."+
	"\n A escala de tempo deve ser a mesma no TEC e no TS.")
	media = 0
	while(tec_det):
		print("Insira o TEC: ", end="")
		try:
			valor_informado = float(input())
			if(valor_informado <= 0.0):
				raise TypeError("Insira um número >= 0.") 
			media = valor_informado
			break
		except:
			erro("O valor do TEC deve ser numérico e maior que 0.")	
	while(tec_det):
		print("Insira o tipo de distribuicao [normal, exponencial ou poisson]: ", end="")
		try:
			valor_informado = input().strip().lower()
			if(valor_informado == "normal"):
				arr_prob_tec = distribuicao_normal(media)
			elif(valor_informado == "exponencial"):
				arr_prob_tec = distribuicao_exponencial(media)
			elif(valor_informado == "poisson"):
				arr_prob_tec = distribuicao_poisson(media)
			else:
				raise TypeError("Opcoes invalidas") 
			break
		except:
			erro("Opção inválida")	
	while(ts_det):
		print("Insira o TS: ", end="")
		try:
			valor_informado = float(input())
			if(valor_informado <= 0.0):
				raise TypeError("Insira um número >= 0.") 
			media = valor_informado
			break
		except:
			erro("O valor do TS deve ser numérico e maior que 0.")
	while(ts_det):
		print("Insira o tipo de distribuicao [normal, exponencial ou poisson]: ", end="")
		try:
			valor_informado = input().strip().lower()
			if(valor_informado == "normal"):
				arr_prob_ts = distribuicao_normal(media)
			elif(valor_informado == "exponencial"):
				arr_prob_ts = distribuicao_exponencial(media)
			elif(valor_informado == "poisson"):
				arr_prob_ts = distribuicao_poisson(media)
			else:
				raise TypeError("Opcoes invalidas") 
			break
		except:
			erro("Opção inválida")	

def cria_probabilidades_amostral():
	global arr_prob_tec, arr_prob_ts
	if (not (ts_det or tec_det)):
		arr_prob_tec = gera_classes_prob([val[0] for val in arr_entradas])
		arr_prob_ts = gera_classes_prob([val[1] for val in arr_entradas])
	elif(not ts_det):
		arr_prob_ts = gera_classes_prob(arr_entradas)
	else:
		arr_prob_tec = gera_classes_prob(arr_entradas)

def gera_classes_prob(arr_valores):
	arr = remove_outliers(arr_valores)
	max = np.max(arr) + 1
	min = np.min(arr)
	step_values = np.linspace(min, max, num=10)
	occour_arr = []
	total = len(arr)
	for val in range(0, len(step_values)-1):
		min_val = step_values[val]
		max_val = step_values[val+1]
		#occour_arr = ([intervalo], media, prob)
		occour_arr.append([[min_val, max_val], (min_val+max_val)/2.0, (len([x for x in arr if (x >= min_val and x < max_val)]))/float(total)])
	occour_arr.sort(key = lambda x: x[2])
	for val in range(1, len(occour_arr)):
		occour_arr[val][2] += occour_arr[val-1][2]
	print("\nTabela de probabilidade acumulada:")
	print("  Intervalo\t\t| Media  | Probabilidade Acumulada")
	for pr in occour_arr:
		print("[{:.4f}],[{:.4f}] \t| {:.4f} |\t {:.4f}".format(pr[0][0], pr[0][1], pr[1], pr[2]))
	print("")
	return occour_arr

def remove_outliers(x, outlierConstant = 1.5):
	a = np.array(x)
	upper_quartile = np.percentile(a, 75)
	lower_quartile = np.percentile(a, 25)
	IQR = (upper_quartile - lower_quartile) * outlierConstant
	quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
	resultList = [y for y in a.tolist() if (y >= quartileSet[0] and y <= quartileSet[1])]
	return resultList

def simula_evento(tipo = None):
	if(tipo == "chegada"):
		result = verifica_classe(arr_prob_tec, random.random())
	if(tipo == "saida"):
		result = verifica_classe(arr_prob_ts, random.random())
	return result

def verifica_classe(arr, val):
	for prob in arr:
		if(val < prob[2]):
			return prob[1]
	raise IndexError("Não foi possível encontrar um valor para a probabilidade encontrada")

def warning(str):
	print("Atenção! ",str)

def erro(str):
	print("Erro! ",str)

def distribuicao_normal(media):
	desvio = -1
	while True:
		print("Informe o desvio padrão: ", end="")
		try:
			desvio = float(input().strip())
			if(desvio < 0):
				raise TypeError
			break
		except:
			erro("O desvio padrão deve ser um valor numérico >= 0")
	s = np.random.normal(media, desvio, 200)
	return gera_classes_prob(s)

def distribuicao_exponencial(media):
	s = np.random.exponential(media, 200)
	return gera_classes_prob(s)

def distribuicao_poisson(media):
	rng = np.random.default_rng()
	s = rng.poisson(media, 200)
	return gera_classes_prob(s)

def chegada():
	global relogio, servidor_em_atendimento, num_cliente, relogio_hc, arr_fila, relogio_hs,cliente_em_atendimento, ultima_chegada
	relogio = relogio_hc
	if (len(arr_fila) >= tam_max_fila):
			warning("A fila está cheia, o cliente foi embora :(")
	elif(not servidor_em_atendimento):
		servidor_em_atendimento = True
		tempo_servico = simula_evento(tipo = "saida")
		relogio_hs = relogio + tempo_servico
		num_cliente += 1
		cliente_em_atendimento = [num_cliente, relogio, tempo_servico]
		registra_evento(tipo="Chegada", num_cliente=cliente_em_atendimento[0], relogio=relogio_hc, chegada = cliente_em_atendimento[1], tec=round(relogio_hc-ultima_chegada, 4))
	else:
		num_cliente += 1
		arr_fila.append([num_cliente, relogio])
		registra_evento(tipo="Chegada", num_cliente=num_cliente, relogio=relogio_hc, chegada = relogio, tec=round(relogio_hc-ultima_chegada, 4))
	ultima_chegada = relogio_hc
	nova_chegada = simula_evento(tipo = "chegada")
	relogio_hc = relogio + nova_chegada

def saida():
	global relogio, relogio_hs, servidor_em_atendimento, arr_fila,cliente_em_atendimento
	if(servidor_em_atendimento):
		registra_evento(tipo="Saida", num_cliente=cliente_em_atendimento[0], relogio=relogio_hs, chegada = cliente_em_atendimento[1], saida=round(relogio_hs, 4)
		, tempo_servico=round(cliente_em_atendimento[2],4), tempo_fila=round(relogio_hs-cliente_em_atendimento[1]-cliente_em_atendimento[2],4))
	relogio = relogio_hs
	if (len(arr_fila) > 0):
		tempo_servico = simula_evento(tipo = "saida")
		cliente_em_atendimento = arr_fila.pop(0)
		cliente_em_atendimento.append(tempo_servico)
		relogio_hs = relogio + tempo_servico
	else:
		servidor_em_atendimento = False
		relogio_hs = float('inf')

ultimo_tec = 0.0
ultimo_ts = 0.0
ultimo_tf = 0.0
def registra_evento(tipo, num_cliente, relogio, chegada, saida="", tempo_servico="", tempo_fila="", tec=""):
	global ultimo_tec, ultimo_ts, ultimo_tf
	verifica_tamanho(arr_tamanhos_fila)
	verifica_tamanho(arr_tamanhos_fila_mean)
	verifica_tamanho(arr_tempos_atendimento)
	verifica_tamanho(arr_tempos_atendimento_mean)
	verifica_tamanho(arr_tempos_espera)
	verifica_tamanho(arr_tempos_espera_mean)
	verifica_tamanho(arr_tempos_chegada)
	verifica_tamanho(arr_tempos_chegada_mean)
	arr_tamanhos_fila.append(len(arr_fila))
	arr_tamanhos_fila_mean.append(np.mean(arr_tamanhos_fila))
	if (tempo_servico != ""):
		ultimo_ts = abs(float(tempo_servico))
	if (tempo_fila != ""):
		ultimo_tf = abs(float(tempo_fila))
	if (tec != ""):
		ultimo_tec = abs(float(tec))
	arr_tempos_atendimento.append(ultimo_ts)
	arr_tempos_atendimento_mean.append(np.mean(arr_tempos_atendimento))
	arr_tempos_espera.append(ultimo_tf)
	arr_tempos_espera_mean.append(np.mean(arr_tempos_espera))
	arr_tempos_chegada.append(ultimo_tec)
	arr_tempos_chegada_mean.append(np.mean(arr_tempos_chegada))
	if(len(buffer_csv) < 15):
		buffer_csv.append((round(relogio, 4), tipo, num_cliente, len(arr_fila), round(chegada,4), saida, tempo_servico, tempo_fila))
	else:
		buffer_csv.append((round(relogio, 4), tipo, num_cliente, len(arr_fila), round(chegada,4), saida, tempo_servico, tempo_fila))
		despeja_csv()

def verifica_tamanho(self):
	if(len(self) > 150):
		self.pop(0)

def despeja_csv():
	global nome_arquivo
	if (nome_arquivo == ""):
		nome_arquivo = "trabalho01_MS_" + dt.now().strftime("%d_%m_%Y__%H_%M_%S") +'.csv'
		with open(nome_arquivo, 'w', newline='') as out_file:
			writer = csv.writer(out_file)
			writer.writerow(('Relogio', 'Evento', 'Cliente', 'Tam. Fila', 'Chegada', 'Saida', 'Tempo Servico', 'Tempo Fila'))
	with open(nome_arquivo, 'a', newline='') as out_file:
		writer = csv.writer(out_file)
		writer.writerows(buffer_csv)
	buffer_csv.clear

def atende():
	if(relogio_hc < relogio_hs):
		#print("Chegada")
		chegada()
	else:
		#print("SAida")
		saida()

def animate(i):
	ax1.clear()
	ax1.plot(arr_tamanhos_fila, label="Tamanho da fila")
	ax1.plot(arr_tamanhos_fila_mean, label="Tamanho médio da fila")
	ax2.clear()
	ax2.plot(arr_tempos_chegada, label="Tempo entre chegadas")
	ax2.plot(arr_tempos_chegada_mean, label="Tempo médio entre chegadas")
	ax3.clear()
	ax3.plot(arr_tempos_atendimento, label="Tempo de atendimento")
	ax3.plot(arr_tempos_atendimento_mean, label="Tempo médio de atendimento")
	ax4.clear()
	ax4.plot(arr_tempos_espera, label="Tempo de espera")
	ax4.plot(arr_tempos_espera_mean, label="Tempo médio de espera")
	ax1.set_title('Tamanho da fila')
	ax4.set_title('Tempo de Espera')
	ax3.set_title('Tempo de atendimento')
	ax2.set_title('Tempo entre chegadas')
	ax1.legend()
	ax2.legend()
	ax3.legend()
	ax4.legend()

style.use('fivethirtyeight')
fig=plt.figure()
ax1 = plt.subplot2grid((10,2),(5,0), rowspan=6, colspan=1)
ax2 = plt.subplot2grid((10,2),(0,0), rowspan=4, colspan=1)
ax3 = plt.subplot2grid((10,2),(0,1), rowspan=4, colspan=1)
ax4 = plt.subplot2grid((10,2),(5,1), rowspan=6, colspan=1)

class ThreadingExample(object):


    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            atende()
            time.sleep(self.interval)

if __name__ == "__main__":
	relogio = 0.0
	mostra_menu()
	if(not (tec_det and ts_det)):
		ler_entradas()
		cria_probabilidades_amostral()
	if(tec_det or ts_det):
		ler_det()
	t = ThreadingExample()
	ani = animation.FuncAnimation(fig, animate, interval=100)
	plt.show()
	despeja_csv()
	print("Os resultados da simulação estão disponíveis no arquivo", nome_arquivo)
	pass
	