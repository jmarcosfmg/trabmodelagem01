import numpy as np
import random

relogio = 0.0
relogio_hc = 0.0
relogio_hs = 0.0
tec_det = False
ts_det = False
num_cliente = 1
servidor_em_atendimento = False
tam_max_fila = float('inf')
arr_entradas = []
arr_atendidos = []
arr_fila = []
arr_prob_tec = []
arr_prob_ts = []

def mostra_menu(estado = None):
	global tec_det, ts_det, tam_max_fila
	print("Menu:")
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

def ler_entradas():
	global arr_entradas
	print("Para cada novo evento, informe os dados", end="")
	if (not(tec_det and ts_det)): 
		print(" da seguinte forma: TEC [ESPAÇO] TS", end="")
	print(", seguidos pela tecla ENTER.")
	print("Para finalizar a inserção dos dados, digite 'done' e aperte ENTER")
	valor_informado = input()
	while(valor_informado.strip().upper() != "DONE"):
		valor_informado = valor_informado.strip()
		if (tec_det and ts_det): 
			try:
				tec_, ts_ = valor_informado.split(' ')
				tec_ = float(tec_.strip())
				ts_ = float(ts_.strip())
				arr_entradas.append((tec_,ts_))
			except:
				warning("Os tempos entre chegadas e o tempo de serviço devem ser valores numérico.")
		elif(tec_det):
			try:
				tec_ = float(valor_informado)
				arr_entradas.append(tec_)
			except:
				warning("O tempo entre chegadas deve ser um valor numérico.")
				continue
		else:
			try:
				ts_ = float(valor_informado)
				arr_entradas.append(ts_)
			except:
				warning("O tempo de serviço deve ser um valor numérico.")
		valor_informado = input()

def ler_det():
	global arr_prob_tec, arr_prob_ts
	warning("Os valores devem preenchidos usando o tempo.\nPor exemplo: Se 15 carros chegam por hora, o TEC deve ser 4 (se o tempo for contado em minutos) ou 0.06 (se for contado em horas)."+
	"\n A escala de tempo deve ser a mesma no TEC e no TS.")
	while(tec_det):
		print("Insira o TEC: ", end="")
		try:
			valor_informado = float(input())
			if(valor_informado <= 0.0):
				raise TypeError("Insira um número >= 0.") 
			arr_prob_tec = [[valor_informado, valor_informado], valor_informado, 1.0]
			break
		except:
			erro("O valor do TEC deve ser numérico e maior que 0.")	
	while(ts_det):
		print("Insira o TS: ", end="")
		try:
			valor_informado = float(input())
			if(valor_informado <= 0.0):
				raise TypeError("Insira um número >= 0.") 
			arr_prob_ts = [[valor_informado, valor_informado], valor_informado, 1.0]
			break
		except:
			erro("O valor do TS deve ser numérico e maior que 0.")


def cria_probabilidades():
	global arr_prob_tec, arr_prob_ts
	if (ts_det and tec_det):
		arr_prob_tec = gera_classes_prob([val[0] for val in arr_entradas])
		arr_prob_ts = gera_classes_prob([val[1] for val in arr_entradas])
	elif(ts_det):
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
	print(occour_arr)
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
	result = []
	if(tipo == "chegada"):
		result.append(verifica_classe(arr_prob_tec, random.random()))
	if(tipo == "saida"):
		result.append(verifica_classe(arr_prob_ts, random.random()))
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

def chegada():
	global relogio, servidor_em_atendimento, num_cliente, relogio_hc, arr_fila
	relogio = relogio_hc
	if(not servidor_em_atendimento):
		servidor_em_atendimento = True
		tempo_servico = simula_evento(tipo = "saida")
		relogio_hs = relogio + tempo_servico
		num_cliente += 1
	else:
		if (len(arr_fila) >= tam_max_fila):
			warning("A fila está cheia, o cliente foi embora :(")
		else:
			num_cliente += 1
			arr_fila.append([num_cliente, )
	nova_chegada = simula_evento(tipo = "chegada")
	relogio_hc = relogio + nova_chegada

def saida():
	global relogio, relogio_hs, servidor_em_atendimento, arr_fila
	relogio = relogio_hs
	if (len(arr_fila) > 0):
		cliente = arr_fila.pop(0)
		tempo_servico = simula_evento(tipo = "saida")
		relogio_hs = relogio + tempo_servico
	else:
		servidor_em_atendimento = False
		relogio_hs = float('inf')

def registra_evento(tipo, num_cliente, tempo_fila)

def atende():
	if(relogio_hc < relogio_hs):
		chegada()
	else:
		saida()
	

if __name__ == "__main__":
	relogio = 0.0
	mostra_menu()
	if(tec_det or ts_det):
		ler_entradas()
		cria_probabilidades()
	elif(not (tec_det and ts_det)):
		ler_det()
	while True:
		atende()
	

	pass
	