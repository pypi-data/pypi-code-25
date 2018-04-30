""# -*- coding: utf-8 -*
'''
    Consulta automatizada ao SIAPA
'''

from collections import namedtuple
from getpass import getpass
import os
import sys
import time

from brazilnum.cpf import validate_cpf
import colorama
from colorama import Fore, Style
import pandas as pd
from selenium.webdriver import Chrome, Firefox, FirefoxOptions, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import (NoSuchElementException,
                                        NoSuchFrameException, TimeoutException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .exceptions import *
from .form_filler import Form


__all__ = ["SPU", "Siapa", "dados_login"]


UF = namedtuple('SPU', ['code', 'name'])

SPU = {"SPUDF": UF("0111", "SPU - DISTRITO FEDERAL"),
       "DF": UF("0110", "DISTRITO FEDERAL"),
       "GO": UF("0120", "GOIAS"),
       "MT": UF("0130", "MATO GROSSO"),
       "MS": UF("0140", "MATO GROSSO DO SUL"),
       "PA": UF("0210", "PARA"),
       "AM": UF("0220", "AMAZONAS"),
       "CE": UF("0310", "CEARA"),
       "MA": UF("0320", "MARANHAO"),
       "PI": UF("0330", "PIAUI"),
       "PE": UF("0410", "PERNAMBUCO"),
       "RN": UF("0420", "RIO GRANDE DO NORTE"),
       "PB": UF("0430", "PARAIBA"),
       "AL": UF("0440", "ALAGOAS"),
       "BA": UF("0510", "BAHIA"),
       "SE": UF("0520", "SERGIPE"),
       "MG": UF("0610", "MINAS GERAIS"),
       "RJ": UF("0710", "RIO DE JANEIRO"),
       "ES": UF("0720", "ESPIRITO SANTO"),
       "SP": UF("0810", "SAO PAULO"),
       "PR": UF("0910", "PARANA"),
       "SC": UF("0920", "SANTA CATARINA"),
       "RS": UF("1010", "RIO GRANDE DO SUL"),
       "AC": UF("0230", "ACRE"),
       "AP": UF("0240", "AMAPA"),
       "RO": UF("0250", "RONDONIA"),
       "RR": UF("0260", "RORAIMA"),
       "TO": UF("0150", "TOCANTINS")}


class Siapa():
    def __init__(self, browser='chrome', headless=False, timeout=5):
        colorama.init()
        self.browser = browser
        self.headless = headless
        self.timeout = timeout

    def entrar(self, numCpf=None, txtSenha=None, modo='producao'):
        if numCpf is None and txtSenha is None:
            numCpf, txtSenha = dados_login()

        self.driver = set_browser(browser=self.browser, headless=self.headless)
        self.wait =  WebDriverWait(self.driver, self.timeout).until

        # Abre o navegador e acessa o site do SIAPA
        url = "https://www.siapa.spu.planejamento.gov.br/"
        urlhom = "http://www.siapahom.serpro.gov.br/"

        # verifica o modo de homologacao
        if modo == 'homologacao':
            self.driver.get(urlhom)
        elif modo == 'producao':
            self.driver.get(url)

        #frame_to_be_available_and_switch_to_it
        self.wait(EC.frame_to_be_available_and_switch_to_it('Principal'))

        formulario = self.formulario()
        formulario.fields['TxtNuCpf'].send_keys(numCpf)
        formulario.fields['TxtSenha'].send_keys(txtSenha)
        formulario.submit()

        # Valida o login
        try:
            LOGIN_OK = (By.XPATH, "//a[text()='Financeiro']")
            self.wait(EC.presence_of_element_located(LOGIN_OK))
        except TimeoutException:
            ERRO = (By.TAG_NAME, 'li')
            error = self.wait(EC.presence_of_element_located(ERRO))

            if error.text == 'USUARIO NAO CADASTRADO':
                msg = 'Usuário {numCpf} não cadastrado.'
                raise UsuarioNaoCadastrado(msg)

            if error.text == 'SENHA NAO OK':
                print(Fore.RED + "Senha inválida. Execute o programa novamente "
                      "com a senha correta." + Style.RESET_ALL)
                raise SenhaInvalida

            if 'SIAPA EM OUTRO TERMINAL' in error.text:
                self.sair()
                self.entrar(numCpf, txtSenha, modo=modo)

    def voltar(self, n=1):
        for i in range(0, n):
            self.driver.back()

    def sair(self):
        if hasattr(self, 'driver'):
            self.driver.close()

    def navigate_menu(self, option1, option2=None, option3=None):

        def click_menu(xpath):
            ''' Clica no menu referente de acordo com o xpath '''
            MENU_XPATH = (By.XPATH, xpath)
            menu = self.wait(EC.visibility_of_element_located(MENU_XPATH))
            menu.click()

        try:
            self.wait(EC.frame_to_be_available_and_switch_to_it('Principal'))
        except TimeoutException:
            pass

        menu_options = []

        menu = f"//*[@id='cabec'][{option1}]"
        menu_options.append(menu + "/a")

        if option2 is not None:
            sub_menu1 = f"{menu}/ul/li[{option2}]"
            menu_options.append(sub_menu1 + "/a")

        if option3 is not None:
            sub_menu2 = f"{sub_menu1}/ul/li[{option3}]"
            menu_options.append(sub_menu2 + "/a")

        for option in menu_options:
            click_menu(option)

    def trocar_GRPU(self, sigla_UF):
        codigo_UF = SPU[sigla_UF].code
        self.navigate_menu(12)

        # aguarda o campo
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "CboGRPU")))

        # busca as opções e seleciona
        opcoes = self.driver.find_elements_by_tag_name("option")
        for opt in opcoes:
            if opt.text.strip().startswith(codigo_UF):
                opt.click()

        # clica no botaão selecionar
        self.driver.find_element_by_name("Avancar").click()
        print(f"GRPU alterada para {sigla_UF} com sucesso.")

    def formulario(self):
        try:
            self.wait(EC.frame_to_be_available_and_switch_to_it('Principal'))
        except (NoSuchFrameException, WebDriverException):
            pass
        formulario = Form(self.driver)
        return formulario

    def links(self):
        ''' Seleciona apenas o links que não estão vinculados a botões utili-
        zando a presença do atributo onmouseover como filtro '''
        try:
            self.wait(EC.frame_to_be_available_and_switch_to_it('Principal'))
        except NoSuchFrameException:
            pass
        page_links = self.driver.find_elements_by_tag_name("a")
        links_list = [l for l in page_links if l.get_attribute("onmouseover") is None]
        return links_list

    def tables(self):
        html = self.driver.page_source
        tabs = pd.read_html(html, header=0, decimal=",", thousands=".")
        return tabs


def set_firefox(headless=False, options=[], download_dir=None):
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference('browser.download.dir', download_dir or os.getcwd())
    firefox_profile.set_preference('browser.download.manager.showWhenStarting', False)
    CONTENT_TYPES = 'application/pdf;application/vnd.ms-excel;text/csv/application/zip'
    firefox_profile.set_preference('browser.helperApps.neverAsk.saveToDisk', CONTENT_TYPES)

    if headless:
        options.append('--headless')

    firefox_options = FirefoxOptions()
    for option in options:
        firefox_options.add_argument(option)

    driver = Firefox(firefox_options=firefox_options,
                     firefox_profile=firefox_profile, log_path="geckodriver.log")
    return driver


def set_browser(browser='chrome', path=None, headless=False, default_directory=None):
    if browser == 'firefox':
        return set_firefox(headless, options=[])

    CHROME_DRIVER = path or 'chromedriver.exe'

    # Configura o browser.
    chrome_options = Options()
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--no-sandbox')

    preferences = {'download.default_directory': default_directory or os.getcwd()}
    chrome_options.add_experimental_option('prefs', preferences)

    if headless is True:
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True

    if os.name == 'posix':
        driver = Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)
    else:
        driver = Chrome(CHROME_DRIVER, chrome_options=chrome_options,
                        service_log_path='driver.log')

    return driver


def dados_login():
    while True:
        cpfServidor = input("Informe o CPF e tecle ENTER: ")
        if validate_cpf(cpfServidor) is True:
            break
        else:
            print(f"{cpfServidor} não é um número de CPF válido.")

    senhaServidor = getpass(prompt="Informe a senha e tecle ENTER: ")
    return cpfServidor, senhaServidor
