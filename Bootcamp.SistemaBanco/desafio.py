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
import textwrap
import time

import redis


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
    -------------------------
    [c]\tCadastrar cliente
    [n]\tCriar nova conta
    [l]\tListar contas
    [q]\tSair
    => """

    return input(textwrap.dedent(texto))


# Rotinas de movimentação da conta
def depositar(saldo, extrato, /):
    """Rotina para depositar um valor na conta do cliente"""
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito:\tR$ {valor:.2f}\n"
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
        extrato += f"Saque:\t\tR$ {valor:.2f}\n"
        numero_saques += 1
        print("=== Saque realizado com sucesso! ===")

    else:
        print("=> Operação falhou! O valor informado é inválido.")

    return saldo, extrato, numero_saques


def exibir_extrato(saldo, /, *, extrato):
    """Rotina para mostrar o extrato do cliente"""
    print("===================== EXTRATO ====================")
    print("Não foram realizadas movimentações.\n" if not extrato else extrato)
    print(f"Saldo:\t\tR$ {saldo:.2f}")
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
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['numero_conta']}
            Titular:\t{conta['cliente']['nome']}
        """
        print("=" * 60)
        print(textwrap.dedent(linha))
    print("=" * 60)


def buscar_cliente(cpf, clientes):
    """Verifica se um CPF existe cadastrado. Caso exista, retorna a pessoa"""
    pessoa = [cliente for cliente in clientes if cliente["cpf"] == cpf]
    return pessoa[0] if pessoa else None


# Rotina principal de controle do sistema
def main():
    """Rotina principal do sistema"""
    qtde_maxima_saques = 3
    valor_maximo_por_saque = 500
    clientes = []
    contas = []
    agencia = "0001"

    # Verifica se há algum dado no Redis. Se houver, recupera, caso contrário, inicializa.
    if not verificar_redis():
        inicializar_redis(0, 0, "")
    saldo, saques_realizados, extrato = obter_dados_redis()  # pylint: disable-msg=C0103

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
                limite=valor_maximo_por_saque,
                numero_saques=saques_realizados,
                limite_saques=qtde_maxima_saques,
            )

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "c":
            criar_cliente(clientes)

        elif opcao == "n":
            numero_conta = len(contas) + 1
            criar_conta(agencia, numero_conta, clientes, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(
                "Operação inválida, por favor selecione novamente a operação desejada."
            )


# Executa o loop principal
cache = redis.Redis(host="redis", port=6379)

limpar_tela()
main()
