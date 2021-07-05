import pandas as pd
import os
from datetime import datetime
from time import sleep

import coleta_filometro

CAMINHO_PROJETO = 'E:\\Lucas\\Programacao\\coleta-filometro-sp'


def main():
    df_situacao_postos = coleta_filometro.coletar_filas_agora()

    arquivo_pickle = '{}.pickle'.format(datetime.now().strftime('%Y_%m_%d_%H_00'))

    df_situacao_postos.to_pickle(os.path.join(CAMINHO_PROJETO, 'dados_pickle', arquivo_pickle))


if __name__ == '__main__':
	try:
		main()
	except:
		while True:
			sleep(3)
			print('Erro')