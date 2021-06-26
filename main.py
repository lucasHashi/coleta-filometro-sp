import pandas as pd
from sqlalchemy import create_engine

import coleta_filometro


def main():
    df_situacao_postos = coleta_filometro.coletar_filas_agora()

    engine = create_engine('sqlite:///./db_filometro.db')
    df_situacao_postos.to_sql('situacao_postos_sp', engine, if_exists='append')





if __name__ == '__main__':
    main()