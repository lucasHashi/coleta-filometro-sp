import pandas as pd
import numpy as np

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

import logging
logging.basicConfig(level=logging.INFO)

import os
import re

URL_BASE_FILOMETRO = 'https://deolhonafila.prefeitura.sp.gov.br/'

MODO_DE_TESTES = True

CAMINHO_PROJETO = 'E:\\Lucas\\Programacao\\coleta-filometro-sp'


def main():
    df_situacao_postos = coletar_filas_agora()

    print(df_situacao_postos)


def coletar_filas_agora():
    logging.info('Iniciando webdriver')
    if(not MODO_DE_TESTES):
        #GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
        #CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
        
        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.binary_location = GOOGLE_CHROME_PATH
        
        #driver_filometro = webdriver.Chrome(execution_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        
        # Para rodar no Heroku
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver_filometro = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    else:
        # Pra rodar em casa
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")

        driver_filometro = webdriver.Chrome(os.path.join(CAMINHO_PROJETO, 'chromedriver.exe'), chrome_options=chrome_options)
        #driver_filometro = webdriver.Firefox()
    
    logging.info('Acessando pagina')
    driver_filometro.get(URL_BASE_FILOMETRO)
    driver_filometro.implicitly_wait(5)

    _ = WebDriverWait(driver_filometro, 10, 2).until(EC.presence_of_element_located((By.ID, 'corpo')))

    divs_categorias = driver_filometro.find_elements_by_css_selector('div#corpo div.container.crss')

    logging.info('Carregando dados')
    dados_situacao_postos = []
    for div_categoria in divs_categorias:
        span_categoria_titulo = div_categoria.find_element_by_css_selector('span.crs').text
        span_categoria_titulo = span_categoria_titulo.strip().lower()

        divs_locais = div_categoria.find_elements_by_css_selector('div.collapse.msg')

        if not divs_locais:
            for div_categoria_aux in div_categoria.find_elements_by_css_selector('div'):
                try:
                    div_local_aux = div_categoria_aux.find_element_by_css_selector('div.container')

                    divs_locais.append(div_local_aux)
                except:
                    pass

        logging.info('  Categoria {}'.format(span_categoria_titulo))
        for div_local in divs_locais:
            titulo, modalidade = div_local.find_elements_by_css_selector('div h6')
            
            descricao, situacao, ultima_atualizacao = div_local.find_elements_by_css_selector('div h11')
            
            titulo = limpar_titulo(titulo.get_attribute('innerHTML'))
            modalidade = limpar_modalidade(modalidade.get_attribute('innerHTML'))
            endereco, cep, telefone_1, telefone_2 = limpar_descricao(descricao.get_attribute('innerHTML'))
            situacao = limpar_situacao(situacao.get_attribute('innerHTML'))
            data_atualizacao, horario_atualizacao = limpar_ultima_atualizacao(ultima_atualizacao.get_attribute('innerHTML'))

            logging.info('    {}'.format(titulo))
            dados_situacao_postos.append({
                'categoria': span_categoria_titulo,
                'titulo': titulo,
                'modalidade': modalidade,
                'endereco': endereco,
                'cep': cep,
                'telefone_1': telefone_1,
                'telefone_2': telefone_2,
                'situacao': situacao,
                'data_atualizacao': data_atualizacao,
                'horario_atualizacao': horario_atualizacao
            })
    
    driver_filometro.close()

    df_situacao_postos = pd.DataFrame(dados_situacao_postos)

    df_situacao_postos['horario_aproximado'] = df_situacao_postos['horario_atualizacao'].apply(aproximar_horario)

    return df_situacao_postos



def limpar_titulo(titulo):
    titulo = titulo.strip().lower()

    return titulo

def limpar_modalidade(modalidade):
    modalidade = modalidade.strip().lower()
    modalidade = modalidade.replace('modalidade:', '').strip()

    normalizacao_modalidades = {
        'posto fixo': 'posto_fixo',
        'posto volante': 'post_volante',
        'drive-thru': 'drive_thru',
        'megaposto': 'megaposto'
    }

    modalidade = normalizacao_modalidades[modalidade]

    return modalidade

def limpar_descricao(descricao):
    descricao = descricao.strip().lower()
    descricao = descricao.replace('endere??o:', '')
    descricao = descricao.replace(':', '')

    # Separar endereco e CEP
    if 'cep' in descricao:
        endereco, cep = re.split("cep", descricao)
    else:
        endereco = descricao
        cep = False

    # Limpando endereco
    endereco = endereco.strip()
    # retira " -" do final
    endereco = endereco[:-2] if re.search(' -$', endereco) else endereco

    if cep:
        # Separar CEP e Tel
        cep = cep.replace('fone', 'tel')
        if 'tel' in cep:
            cep, telefone = re.split("tel", cep)

            # Limpando CEP
            cep = cep.replace(' ', '')
            cep = cep.replace('-', '')

            # Limpando tel
            telefone = telefone.replace(' ', '')
            telefone = telefone.replace('-', '')

            telefones = re.split('/', telefone)

            telefone_1 = telefones[0] if len(telefones) >= 1 else np.nan
            telefone_2 = telefones[1] if len(telefones) >= 2 else np.nan
        else:
            telefone_1 = np.nan
            telefone_2 = np.nan
    else:
        cep = np.nan
        telefone_1 = np.nan
        telefone_2 = np.nan

    return endereco, cep, telefone_1, telefone_2

def limpar_situacao(situacao):
    situacao = situacao.strip().lower()
    situacao = situacao.replace('situa????o:', '').strip()

    situacao = {
        'n??o funcionando': 'nao_funcionando',
        'fila grande': 'fila_grande',
        'fila m??dia': 'fila_media',
        'fila pequena': 'fila_pequena',
        'sem fila': 'sem_fila',
        'aguardando abastecimento': 'aguardando_abastecimento',
        '': 'sem_informacao',
        'null': 'sem_informacao'
    }[situacao]

    return situacao

def limpar_ultima_atualizacao(ultima_atualizacao):
    ultima_atualizacao = ultima_atualizacao.strip().lower()
    ultima_atualizacao = ultima_atualizacao.replace('??ltima informa????o:', '').strip()

    try:
        data, horario = ultima_atualizacao.split()
        return data, horario
    except:
        return np.nan, np.nan

def aproximar_horario(horario_texto):
    try:
        hora, minuto = horario_texto.split(':')
    except:
        return np.nan, np.nan

    hora = int(hora)
    minuto = int(minuto)

    # Se minuto for antes das 45, arredonda pra antes
    # Se nao arredonda pra frente, se for 24h passa pra 0h
    hora = hora if minuto <= 45 else hora+1 if hora != 24 else 0

    # Passa a hora para string
    hora = str(hora) if hora >= 10 else '0'+str(hora)

    return hora+':00'


if __name__ == '__main__':
    main()
