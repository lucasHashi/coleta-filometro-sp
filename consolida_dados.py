import pandas as pd
import os

CAMINHO_PROJETO = 'E:\\Lucas\\Programacao\\coleta-filometro-sp'
CAMINHO_PROJETO = 'C:\\Users\\lucas.belmonte\\Documents\\GitHub\\coleta-filometro-sp'


def main():
    df_dados_consolidados = consolidar_dados_situacao_sp()

    df_dados_consolidados.to_csv('dados_consolidados.csv', index=False)


def consolidar_dados_situacao_sp():
    #listas arquivos em dados_pickle
    arquivos_dados = os.listdir(os.path.join(CAMINHO_PROJETO, 'dados_pickle'))
    df_completo_situacao_postos_sp = []
    for arquivo in arquivos_dados:
        df_atual = pd.read_pickle(os.path.join(CAMINHO_PROJETO, 'dados_pickle', arquivo))

        df_completo_situacao_postos_sp.append(df_atual)
    
    df_completo_situacao_postos_sp = pd.concat(df_completo_situacao_postos_sp, ignore_index=True)

    return df_completo_situacao_postos_sp


if __name__ == '__main__':
    main()