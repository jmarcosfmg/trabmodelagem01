import numpy as np
import random
from datetime import datetime as dt
import threading
import operator
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

relogio = 0.0
relogio_hc = 0.0
relogio_hs = float('inf')
ultima_chegada = 0.0
tec_det = True
ts_det = True
num_cliente = 0
lista_servidores = []
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
	global tec_det, ts_det, tam_max_fila, lista_servidores
	print("\n\nMenu:")
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
	while True:
		print("Insira o número de atendentes [1-9]")
		try:
			resp = int(input())
			if(resp < 1 or resp > 9):
				raise TypeError("Insira um valor entre 1 e 9")
			lista_servidores = [Servidor(i) for i in range(0,resp)]
			break
		except:
			erro("Insira um valor entre 1 e 9.")
		
	print("")

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
			arr_prob_tec = distribuicao_exponencial(valor_informado)
			break
		except:
			erro("O valor do TEC deve ser numérico e maior que 0.")	
	
	while(ts_det):
		print("Insira o TS: ", end="")
		try:
			valor_informado = float(input())
			if(valor_informado <= 0.0):
				raise TypeError("Insira um número >= 0.") 
			arr_prob_ts = distribuicao_exponencial(valor_informado)
			break
		except:
			erro("O valor do TS deve ser numérico e maior que 0.")
	
def gera_classes_prob(arr):
	max = np.max(arr) + 1
	min = np.min(arr)
	step_values = np.linspace(min, max, num=10)
	occour_arr = []
	total = len(arr)
	for val in range(0, len(step_values)-1):
		min_val = step_values[val]
		max_val = step_values[val+1]
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


def distribuicao_exponencial(media):
	s = np.random.uniform(size=200)
	lambda_ = 1/media
	aux = list(map(lambda b: -(np.log(1-b))/lambda_, s))
	print(aux)
	return gera_classes_prob(aux)

def servidores_ocupados():
	return all(serv.em_atendimento == True for serv in lista_servidores)

def atende_cliente(cliente):
	global lista_servidores, cliente_em_atendimento, relogio_hs
	servidor = np.random.choice([serv for serv in lista_servidores if serv.em_atendimento == False])
	servidor.atende(cliente)
	cliente_em_atendimento.append(cliente)
	cliente_em_atendimento.sort(key = operator.attrgetter('saida'))
	relogio_hs = cliente_em_atendimento[0].saida


## adicionar no cliente qual servidor o está atendendo (talvez criar uma classe para o cliente)
## servidor em atendimento deve ser array

def chegada():
	global relogio, num_cliente, relogio_hc, arr_fila, ultima_chegada
	relogio = relogio_hc
	if (len(arr_fila) >= tam_max_fila):
			warning("A fila está cheia, o cliente foi embora :(")
	elif(not servidores_ocupados()):
		num_cliente += 1
		novo_cliente = Cliente(num_cliente, relogio_hc)
		atende_cliente(novo_cliente)
		registra_evento(tipo="Chegada", num_cliente=num_cliente, relogio=relogio, chegada = novo_cliente.chegada, tec=round(relogio_hc-ultima_chegada, 4))
	else:
		num_cliente += 1
		novo_cliente = Cliente(num_cliente, relogio_hc)
		arr_fila.append(novo_cliente)
		registra_evento(tipo="Chegada", num_cliente=num_cliente, relogio=relogio_hc, chegada = relogio, tec=round(relogio_hc-ultima_chegada, 4))
	ultima_chegada = relogio_hc
	nova_chegada = simula_evento(tipo = "chegada")
	relogio_hc = relogio + nova_chegada

def saida():
	global relogio, relogio_hs, lista_servidores, arr_fila, cliente_em_atendimento
	if(len(cliente_em_atendimento) > 0):
		cliente = cliente_em_atendimento.pop(0)
		lista_servidores[cliente.servidor].finaliza_atendimento(cliente)
		registra_evento(tipo="Saida", num_cliente=cliente.num_cliente, relogio=relogio_hs, chegada = cliente.chegada, saida=round(relogio_hs, 4)
		, tempo_servico=round(cliente.tempo_servico,4), tempo_fila=round(relogio_hs-cliente.chegada-cliente.tempo_servico,4), servidor=cliente.servidor)
	relogio = relogio_hs
	if (len(arr_fila) > 0):
		novo_cliente = arr_fila.pop(0)
		atende_cliente(novo_cliente)
	if(len(cliente_em_atendimento) == 0):
		relogio_hs = float('inf')

ultimo_tec = 0.0
ultimo_ts = 0.0
ultimo_tf = 0.0
def registra_evento(tipo, num_cliente, relogio, chegada, saida="", tempo_servico="", tempo_fila="", tec="", servidor=""):
	global ultimo_tec, ultimo_ts, ultimo_tf
	verifica_limites_arrays()
	arr_tamanhos_fila_mean.append(calcula_media(arr_tamanhos_fila_mean, len(arr_fila)))
	arr_tamanhos_fila.append(len(arr_fila))
	if (tempo_servico != ""):
		ultimo_ts = abs(float(tempo_servico))
	if (tempo_fila != ""):
		ultimo_tf = abs(float(tempo_fila))
	if (tec != ""):
		ultimo_tec = abs(float(tec))
	arr_tempos_atendimento_mean.append(calcula_media(arr_tempos_atendimento_mean, ultimo_ts))
	arr_tempos_atendimento.append(ultimo_ts)
	arr_tempos_espera_mean.append(calcula_media(arr_tempos_espera_mean, ultimo_tf))
	arr_tempos_espera.append(ultimo_tf)
	arr_tempos_chegada_mean.append(calcula_media(arr_tempos_chegada_mean, ultimo_tec))
	arr_tempos_chegada.append(ultimo_tec)
	buffer_csv.append((round(relogio, 4), tipo, num_cliente, len(arr_fila), round(chegada,4), saida, tempo_servico, tempo_fila, servidor))
	if(len(buffer_csv) > 15):
		despeja_csv()

def calcula_media(arr, novoval):
	tam = len(arr)+1
	if (tam == 1):
		return novoval
	return ((arr[-1] * (tam-1)) + novoval)/float(tam)

def verifica_limites_arrays():
	verifica_tamanho(arr_tamanhos_fila)
	verifica_tamanho(arr_tamanhos_fila_mean)
	verifica_tamanho(arr_tempos_atendimento)
	verifica_tamanho(arr_tempos_atendimento_mean)
	verifica_tamanho(arr_tempos_espera)
	verifica_tamanho(arr_tempos_espera_mean)
	verifica_tamanho(arr_tempos_chegada)
	verifica_tamanho(arr_tempos_chegada_mean)

def verifica_tamanho(self):
	if(len(self) > 150):
		self.pop(0)

def despeja_csv():
	global nome_arquivo
	if (nome_arquivo == ""):
		nome_arquivo = "trabalho01_MS_" + dt.now().strftime("%d_%m_%Y__%H_%M_%S") +'.csv'
		with open(nome_arquivo, 'w', newline='') as out_file:
			writer = csv.writer(out_file)
			writer.writerow(('Relogio', 'Evento', 'Cliente', 'Tam. Fila', 'Chegada', 'Saida', 'Tempo Servico', 'Tempo Fila', 'Servidor'))
	with open(nome_arquivo, 'a', newline='') as out_file:
		writer = csv.writer(out_file)
		writer.writerows(buffer_csv)
	buffer_csv.clear

def atende():
	if(relogio_hc < relogio_hs):
		print("Chegada -- {}".format(relogio_hc))
		chegada()
	else:
		print('Saida -- {}'.format(relogio_hs))
		saida()
	print("Atendentes = ", ["Ocupado" if serv.em_atendimento == True else "Livre" for serv in lista_servidores])
	print("Clientes em atendimento = ", [cl.num_cliente for cl in cliente_em_atendimento])
	print("Fila de atendimento = ", [cl.num_cliente for cl in arr_fila], "\n")


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

class Servidor(object):
	def __init__(self, num_servidor):
		self.num_servidor = num_servidor
		self.em_atendimento = False
		self.tempo_trabalhado = 0.0
	
	def atende(self, cliente):
		tempo_servico = simula_evento(tipo = "saida")
		self.tempo_trabalhado += tempo_servico
		self.em_atendimento = True
		cliente.registraAtendimento(self.num_servidor, tempo_servico)

	def finaliza_atendimento(self, cliente):
		self.em_atendimento = False
		


class Cliente(object):
	def __init__(self, num_cliente, chegada):
		self.num_cliente = num_cliente
		self.chegada = chegada
	
	def registraAtendimento(self, servidor, tempo_servico):
		self.saida = relogio + tempo_servico
		self.servidor = servidor
		self.tempo_servico = tempo_servico

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
	ler_det()
	t = ThreadingExample()
	ani = animation.FuncAnimation(fig, animate, interval=100)
	plt.show()
	despeja_csv()
	print("\n-----------------------------------------------")
	print("---------------- RELATÓRIO --------------------")
	print("Tempo da simulação = {:.3f} ------------------".format(relogio))
	print("Tempo médio de atendimento = {:.3f} ------------".format(arr_tempos_atendimento_mean[-1]))
	print("tamanho médio da fila = {:.3f} -----------------".format(arr_tamanhos_fila_mean[-1]))
	print("Tempo médio entre chegadas = {:.3f} ------------".format(arr_tempos_chegada_mean[-1]))
	print("Tempo médio de espera = {:.3f} -----------------".format(arr_tempos_espera_mean[-1]))
	print("Estatísticas dos servidores -------------------")
	print("Servidor|  Tempo Ocioso | Tempo Trabalhado")
	print("-----------------------------------------------")
	for serv in lista_servidores:
		print("{} \t| {:.3f} \t| {:.3f}\t".format(serv.num_servidor, relogio-serv.tempo_trabalhado, serv.tempo_trabalhado))
		print("\t| {:.3f}% \t| {:.3f}%\t".format((relogio-serv.tempo_trabalhado)*100/relogio, serv.tempo_trabalhado*100/relogio))
		print("-----------------------------------------------")
	print("-----------------------------------------------")
	print("Os resultados da simulação estão disponíveis no arquivo", nome_arquivo)
	pass
	