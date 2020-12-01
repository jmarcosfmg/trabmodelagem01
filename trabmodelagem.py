import numpy as np

tec_det = False
ts_det = False
tam_max_fila = float('inf')
arr_entradas = []

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
					print("Erro!\n")
		if (x == "N" or x == "S"):
			break

def ler_entradas():
	ultima_chegada = 0.0
	ultima_saida = 0.0
	relogio = 0.0
	fila_atual = []
	print("Para cada novo evento, informe os dados aleatórios", end="")
	if (tec_det and ts_det): 
		print(" da seguinte forma: TEC [ESPAÇO] TS", end="")
	print(" seguidos pela tecla ENTER.")
	print("Para finalizar a inserção dos dados, digite 'done' e aperte ENTER")
	valor_informado = input().upper()
	while(valor_informado.strip() != "DONE"):
		valor_informado = valor_informado.strip()
		tec_, tse_ = valor_informado.split(' ')
		if(lim_fila):
			if(tam_atual_fila >= tam_max_fila):
				continue
		arr_entradas.append(tec_,tse_)			
		


mostra_menu()
	