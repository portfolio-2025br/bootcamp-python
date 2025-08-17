#!/usr/bin/env python3

# ################################################################################
#  Copyright (c) 2025  Claudio André <portfolio-2025br at claudioandre.slmail.me>
#              ___                _      ___       _
#             (  _`\             ( )_  /'___)     (_ )  _
#             | |_) )  _    _ __ | ,_)| (__   _    | | (_)   _
#             | ,__/'/'_`\ ( '__)| |  | ,__)/'_`\  | | | | /'_`\
#             | |   ( (_) )| |   | |_ | |  ( (_) ) | | | |( (_) )
#             (_)   `\___/'(_)   `\__)(_)  `\___/'(___)(_)`\___/'
#
# This program comes with ABSOLUTELY NO WARRANTY; express or implied.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, as expressed in version 2, seen at
# https://www.gnu.org/licenses/gpl-2.0.html
# ################################################################################
# Sistema bancário de Exemplo
# More info at https://github.com/portfolio-2025br/bootcamp-python

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
import textwrap
import time

import redis

AGENCIA = "0001"
QTDE_MAXIMA_SAQUES = 3
VALOR_MAXIMO_POR_SAQUE = 500


# Rotinas Redis
def inicializar_redis(valor_saldo, qtde_saques, texto_extrato):
    """Inicializa o Redis com dados de uma conta bancária padrão"""
    salvar_dados_redis(valor_saldo, qtde_saques, texto_extrato)


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


def salvar_dados_redis(valor_saldo, qtde_saques, texto_extrato):
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


def verificar_redis() -> bool:
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


# Rotinas de controle da tela
def limpar_tela():
    """Limpa a tela em diferentes sistemas operacionais"""
    os.system("cls" if os.name == "nt" else "clear")


def menu():
    """Mostra o menu principal do sistema"""
    texto = """\n
    ====================== MENU ======================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
       \t-----------------
    [c]\tCadastrar cliente
    [n]\tCriar nova conta
    [l]\tListar contas
       \t-----------------
    [q]\tSair
       \t=> """

    return input(textwrap.dedent(texto))


# Rotinas de movimentação da conta
def depositar(saldo, extrato, /):
    """Rotina para depositar um valor na conta do cliente"""
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito:{f'R$ {valor:.2f}':>41}\n"
        print("=== Depósito realizado com sucesso! ===")
    else:
        print("=> Operação falhou! O valor informado é inválido.")

    return saldo, extrato


def sacar(*, saldo, extrato, limite, numero_saques, limite_saques):
    """Rotina para sacar um valor da conta do cliente"""
    valor = float(input("Informe o valor do saque: "))

    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("=> Operação falhou! Você não tem saldo suficiente.")

    elif excedeu_limite:
        print("=> Operação falhou! O valor do saque excede o limite.")

    elif excedeu_saques:
        print("=> Operação falhou! Número máximo de saques excedido.")

    elif valor > 0:
        saldo -= valor
        extrato += f"Saque:{f'R$ {valor:.2f}':>44}\n"
        numero_saques += 1
        print("=== Saque realizado com sucesso! ===")

    else:
        print("=> Operação falhou! O valor informado é inválido.")

    return saldo, extrato, numero_saques


def exibir_extrato(saldo, /, *, extrato):
    """Rotina para mostrar o extrato do cliente"""
    print("===================== EXTRATO ====================")
    print("Não foram realizadas movimentações.\n" if not extrato else extrato)
    print(f"Saldo:{f'R$ {saldo:.2f}':>44}\n")
    print("==================================================")


# Rotinas de manutenção do cliente e conta
def criar_cliente(clientes):
    """Cria um novo cliente, caso o CPF NÃO exista cadastrado"""
    cpf = input("Informe o CPF (somente número): ")
    cliente = buscar_cliente(cpf, clientes)

    if cliente is None:
        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascimento: ")
        endereco = input("Informe o endereço: ")

        clientes.append(
            {
                "nome": nome,
                "data_nascimento": data_nascimento,
                "cpf": cpf,
                "endereco": endereco,
            }
        )
        print("=== Cliente criado com sucesso! ===")

    else:
        print("=> Já existe um cliente com esse CPF!")


def criar_conta(agencia, numero_conta, clientes, contas):
    """Cria uma nova conta, caso o CPF (cliente) já exista cadastrado"""
    cpf = input("Informe o CPF do usuário: ")
    cliente = buscar_cliente(cpf, clientes)

    if cliente:
        contas.append(
            {"agencia": agencia, "numero_conta": numero_conta, "cliente": cliente}
        )
        print("=== Conta criada com sucesso! ===")
    else:
        print("=> Cliente não encontrado, impossível criar uma conta!")


def listar_contas(contas):
    """Lista todas as contas cadastradas no sistema"""
    for conta in contas:
        linha = f"""\
            Agência:\t{conta["agencia"]}
            C/C:\t\t{conta["numero_conta"]}
            Titular:\t{conta["cliente"]["nome"]}
        """
        print("=" * 50)
        print(textwrap.dedent(linha))
    print("=" * 50)


def buscar_cliente(cpf, clientes):
    """Verifica se um CPF existe cadastrado. Caso exista, retorna a pessoa"""
    pessoa = [cliente for cliente in clientes if cliente["cpf"] == cpf]
    return pessoa[0] if pessoa else None


# Rotina principal de controle do sistema
def main():
    """Rotina principal do sistema"""
    clientes = []
    contas = []

    # Verifica se há algum dado no Redis. Se houver, recupera, caso contrário, inicializa.
    if not verificar_redis():
        inicializar_redis(0, 0, "")
    saldo, saques_realizados, extrato = obter_dados_redis()

    while True:
        salvar_dados_redis(saldo, saques_realizados, extrato)
        opcao = menu()
        limpar_tela()

        if opcao == "d":
            saldo, extrato = depositar(saldo, extrato)

        elif opcao == "s":
            saldo, extrato, saques_realizados = sacar(
                saldo=saldo,
                extrato=extrato,
                limite=VALOR_MAXIMO_POR_SAQUE,
                numero_saques=saques_realizados,
                limite_saques=QTDE_MAXIMA_SAQUES,
            )

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "c":
            criar_cliente(clientes)

        elif opcao == "n":
            numero_conta = len(contas) + 1
            criar_conta(AGENCIA, numero_conta, clientes, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(
                "Operação inválida, por favor selecione novamente a operação desejada."
            )


if __name__ == "__main__":
    cache = redis.Redis(host="redis", port=6379)

    limpar_tela()
    main()
