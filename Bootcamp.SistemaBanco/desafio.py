#!/usr/bin/env python3

"""
Sistema Bancário com Python.

Os dados são salvos em uma instância do Redis
 - e são perdidos quando a instância do Redis for desligada.

    Parameters:
        Nenhum

    Returns:
        Nenhum.
"""

import os
import time

import redis


def validar_redis() -> bool:
    """Verifica se há dados da conta bancária do banco de dados (no Redis)"""
    retries = 3
    while True:
        try:
            return cache.get("live") is not None
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


def initializar_redis(valor_saldo, qtde_saques, texto_extrato):
    """Inicializa o Redis com dados de uma conta bancária padrão"""
    salvar_dados(valor_saldo, qtde_saques, texto_extrato)


def obter_dados_redis():
    """Se existir, obtém os dados da conta bancária do banco de dados (no Redis)"""
    retries = 3
    while True:
        try:
            local_saldo = float(cache.get("saldo").decode("utf-8"))
            local_extrato = cache.get("extrato").decode("utf-8")
            local_numero_saques = float(cache.get("numero_saques").decode("utf-8"))

            return local_saldo, local_numero_saques, local_extrato
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


def salvar_dados(valor_saldo, qtde_saques, texto_extrato):
    """Salva os dados da conta bancária no banco de dados (no Redis)"""
    retries = 3
    while True:
        try:
            cache.set("saldo", valor_saldo)
            cache.set("extrato", texto_extrato)
            cache.set("numero_saques", qtde_saques)
            cache.set("live", 1)

            break
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


def limpar_tela():
    """Limpa a tela em diferentes sistemas operacionais"""
    os.system("cls" if os.name == "nt" else "clear")


# void main(void)
QTDE_MAXIMA_SAQUES = 3
VALOR_MAXIMO_POR_SAQUE = 500
MENU = """

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

cache = redis.Redis(host="redis", port=6379)

# Verifica se há algum dado no Redis. Se houver, recupera, caso contrário, inicializa.
if not validar_redis():
    initializar_redis(0, 0, "")
saldo, saques_realizados, extrato = obter_dados_redis()  # pylint: disable-msg=C0103

while True:
    salvar_dados(saldo, saques_realizados, extrato)
    opcao = input(MENU)
    limpar_tela()

    if opcao == "d":
        valor = float(input("Informe o valor do depósito: "))

        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"

        else:
            print("Operação falhou! O valor informado é inválido.")

    elif opcao == "s":
        valor = float(input("Informe o valor do saque: "))

        excedeu_saldo = valor > saldo

        excedeu_limite = valor > VALOR_MAXIMO_POR_SAQUE

        excedeu_saques = saques_realizados >= QTDE_MAXIMA_SAQUES

        if excedeu_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")

        elif excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: \tR$ {valor:.2f}\n"
            saques_realizados += 1

        else:
            print("Operação falhou! O valor informado é inválido.")

    elif opcao == "e":
        print("\n================ EXTRATO ================")
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"\nSaldo: R$ {saldo:.2f}")
        print("==========================================")

    elif opcao == "q":
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")
