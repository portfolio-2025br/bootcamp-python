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

import json
import os
import textwrap
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import redis

AGENCIA = "0001"
QTDE_MAXIMA_SAQUES = 3
VALOR_MAXIMO_POR_SAQUE = 500.0
ERR_0001 = "=> Cliente não encontrado ou não possui conta!"
MSG_0001 = "Informe o CPF do cliente: "


class JSONSerializableMixin:  # pylint: disable-msg=R0903
    """Classe Mixin para automatizar a serialização de objetos"""

    def obter_json(self) -> str:
        """Método para serializar objetos"""
        return json.dumps(vars(self), cls=DesafioEncoder)


class DesafioEncoder(json.JSONEncoder):
    """Encoder personalizado para as classes do sistema"""

    def default(self, o) -> dict:
        """Método que converte os objetos em strings JSON"""
        if isinstance(o, Cliente):
            return {
                "__type__": "Cliente",
                "id": o.pk,
                "cpf": o.cpf,
                "nome": o.nome,
                "data_nascimento": o.data_nascimento,
                "endereco": o.endereco,
            }
        if isinstance(o, Historico):
            return {"__type__": "Historico", "transacoes": o.transacoes}
        return json.JSONEncoder.default(self, o)


class Historico:
    """Lista contendo o histórico de operações"""

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self) -> list:
        """Retorna as transações registradas"""
        return self._transacoes

    def adicionar_transacao(self, transacao, teste=0):
        """Adiciona uma transação ao histórico"""
        if teste != 0:
            # Permite criar eventos em datas distintas
            nova_data = datetime.now(timezone.utc) + timedelta(days=teste)
            self._transacoes.append(
                {
                    "tipo": transacao.__class__.__name__,
                    "valor": transacao.valor,
                    "data": nova_data.strftime("%d-%m-%Y %H:%M:%S"),
                }
            )

        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        """
        Gera um relatório das transações do tipo (opcional) recebido como parâmetro
        """
        for transacao in self._transacoes:
            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):
                yield transacao

    def transacoes_do_dia(self, filtro) -> list:
        """Gera um relatório das transações que ocorreram no dia recebido como parâmetro"""
        data = filtro.date()
        transacoes = []

        for transacao in self._transacoes:
            data_transacao = datetime.strptime(
                transacao["data"], "%d-%m-%Y %H:%M:%S"
            ).date()

            if data == data_transacao:
                transacoes.append(transacao)

        return transacoes

    def transacoes_de_hoje(self) -> list:
        """Gera um relatório das transações que ocorreram hoje (dia atual)"""
        data_atual = datetime.now(timezone.utc).date()
        return self.transacoes_do_dia(data_atual)


@dataclass
class Cliente(JSONSerializableMixin):
    """Classe que representa e mantém os dados dos clientes"""

    _id: int
    _cpf: str
    _nome: str
    _data_nascimento: str
    _endereco: str

    def __post_init__(self):
        self._id = 0 if self._id is None else self._id

    @classmethod
    def vazio(cls):
        """Construtor sem parâmetros para a classe"""
        return cls(None, None, None, None, None)

    @property
    def pk(self) -> int:
        """ID (identificador único) do objeto (getter)"""
        return self._id

    @pk.setter
    def pk(self, valor):
        """ID (identificador único) do objeto (setter)"""
        self._id = valor

    @property
    def cpf(self) -> str:
        """CPF do cliente"""
        return self._cpf

    @property
    def chave(self) -> str:
        """String usada como chave no Redis"""
        return "total_clientes"

    @property
    def prefixo(self) -> str:
        """String usada como prefixo para gerar a chave de dados no Redis"""
        return "CL_"

    @property
    def nome(self) -> str:
        """Nome do cliente"""
        return self._nome

    @property
    def data_nascimento(self) -> str:
        """Data de Nascimento do cliente"""
        return self._data_nascimento

    @property
    def endereco(self) -> str:
        """Endereço do cliente"""
        return self._endereco

    @property
    def idade(self) -> int:
        """Calcula e retorna a idade do cliente"""
        try:
            nascimento = datetime.strptime(self._data_nascimento, "%d/%m/%Y")
        except ValueError:
            nascimento = datetime.now()
        d = datetime.now() - nascimento

        return d.days // 365

    def salvar(self, clientes) -> bool:
        """Salva (persiste) o objeto no banco de dados"""
        sucesso = PersistenciaDB.salvar(self)

        if sucesso > 0:
            clientes.append(self)
            return True
        return False


@dataclass
class Conta(JSONSerializableMixin):
    """Classe que representa e mantém os dados dos contas das clientes"""

    _id: int
    _cliente: Cliente

    def __post_init__(self):
        self._agencia = AGENCIA
        self._historico = Historico()
        self._saldo = 0.0

    @classmethod
    def vazio(cls):
        """Construtor sem parâmetros para a classe"""
        return cls(None, None)

    @property
    def pk(self) -> int:
        """ID (identificador único) do objeto (getter)"""
        return self._id

    @pk.setter
    def pk(self, valor):
        """ID (identificador único) do objeto (setter)"""
        self._id = valor

    @property
    def agencia(self) -> str:
        """Agência responsável pela conta"""
        return self._agencia

    @property
    def numero_conta(self) -> int:
        """Número da conta"""
        return self.pk

    @property
    def cliente(self) -> Cliente:
        """Cliente proprietário da conta"""
        return self._cliente

    @property
    def saldo(self) -> float:
        """Saldo da conta"""
        return self._saldo

    @property
    def qtde_maxima_saques_dia(self) -> int:
        """Quantidade máxima de saques diários"""
        return QTDE_MAXIMA_SAQUES

    @property
    def valor_maximo_saque(self) -> float:
        """Valor máximo do saque que é permitido"""
        return VALOR_MAXIMO_POR_SAQUE

    @property
    def chave(self) -> str:
        """String usada como chave no Redis"""
        return "total_contas"

    @property
    def prefixo(self) -> str:
        """String usada como prefixo para gerar a chave de dados no Redis"""
        return "CO_"

    @property
    def historico(self) -> Historico:
        """Lista com o histórico de operações da conta

        Returns:
            _type_: Histórico
        """
        return self._historico

    def salvar(self, contas) -> bool:
        """Salva (persiste) o objeto no banco de dados"""
        sucesso = PersistenciaDB.salvar(self)

        if sucesso > 0:
            contas.append(self)
            return True
        return False

    def depositar(self, valor) -> tuple[bool, str]:
        """Realiza a operação depósito no objeto"""
        if valor > 0:
            self._saldo += valor
            return True, "=== Depósito realizado com sucesso ==="
        return False, "==> Operação falhou! O valor informado é inválido!"

    def sacar(self, valor) -> tuple[bool, str]:
        """Realiza a operação saque no objeto"""
        numero_saques = len(
            [
                # Aqui eu precisava fazer group by por dia. Projeto já está complexo o suficiente.
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )
        excedeu_saldo = valor > self._saldo
        excedeu_limite = numero_saques >= self.valor_maximo_saque
        excedeu_quantidade = numero_saques >= self.qtde_maxima_saques_dia

        if excedeu_saldo:
            mensagem = "Operação falhou! Você não tem saldo suficiente."
        elif excedeu_limite:
            mensagem = "===> Operação falhou! Valor permitido para saques excedido!"
        elif excedeu_quantidade:
            mensagem = "===> Operação falhou! Número máximo de saques excedido!"
        elif valor > 0:
            self._saldo -= valor
            mensagem = "=== Saque realizado com sucesso ==="
            return True, mensagem
        else:
            mensagem = "==> Operação falhou! O valor informado é inválido!"

        return False, mensagem


class Transacao(ABC):
    """Classe abstrata para representar as transações"""

    @property
    @abstractmethod
    def valor(self) -> float:
        """Método abstrado para representa o valor da operação"""

    @abstractmethod
    def registrar(self, conta) -> str:
        """Método abstrado que realiza e registra operações na conta"""


class Saque(Transacao):
    """Classe para representar os saques"""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self) -> float:
        """Representa o valor da operação"""
        return self._valor

    def registrar(self, conta) -> str:
        """Realiza e registra a operação na conta"""
        sucesso, mensagem = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)
        return mensagem


class Deposito(Transacao):
    """Classe para representar os depósitos"""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self) -> float:
        """Representa o valor da operação"""
        return self._valor

    def registrar(self, conta) -> str:
        """Realiza e registra a operação na conta"""
        sucesso, mensagem = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self, -1)
        return mensagem


class PersistenciaDB:
    """Classe para encapsular a persistência de dados usando algum mecanismo ou banco de dados"""

    cache = redis.Redis(host="redis", port=6379)

    @classmethod
    def obter_dado(cls, chave) -> str | None:
        """Obtém no DB (Redis) um valor dado uma chave"""
        retries = 3
        while True:
            try:
                retorno = cls.cache.get(chave)
                return str(retorno.decode("utf-8")) if retorno else None
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc
                retries -= 1
                time.sleep(0.5)

    @classmethod
    def salvar_dado(cls, chave, valor) -> bool:
        """Salva uma chave->valor no DB (Redis)"""
        retries = 3
        while True:
            try:
                cls.cache.set(chave, valor)
                return True
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc
                retries -= 1
                time.sleep(0.5)

    @classmethod
    def obter_total_registros(cls, chave) -> int:
        """Obtém o total de registros de uma classe que está salva no DB"""
        total = cls.obter_dado(chave)
        if total is None:
            return 0
        return int(total)

    @classmethod
    def obter(cls, lista, objeto):
        """Obtém os dados de uma classe que está salva no DB"""

        # Obtém a quantidade de registros do tipo(objeto) que estão salvos no banco
        total = cls.obter_total_registros(objeto.chave)

        for posicao in range(1, int(total) + 1):
            conteudo_json = cls.obter_dado(objeto.prefixo + str(posicao))

            if conteudo_json:
                dados = json.loads(conteudo_json)
                if dados:
                    if isinstance(objeto, Cliente):
                        cliente = Cliente(
                            _id=dados["_id"],
                            _cpf=dados["_cpf"],
                            _nome=dados["_nome"],
                            _data_nascimento=dados["_data_nascimento"],
                            _endereco=dados["_endereco"],
                        )
                        lista.append(cliente)
                    elif isinstance(objeto, Conta):
                        cliente = Cliente(
                            _id=dados["_cliente"]["id"],
                            _cpf=dados["_cliente"]["cpf"],
                            _nome=dados["_cliente"]["nome"],
                            _data_nascimento=dados["_cliente"]["data_nascimento"],
                            _endereco=dados["_cliente"]["endereco"],
                        )
                        conta = Conta(_id=dados["_id"], _cliente=cliente)
                        lista.append(conta)
                    else:
                        raise NotImplementedError

                else:
                    print("=> Erro X563!")
            else:
                print("=> Erro X564!")

    @classmethod
    def listar_clientes(cls):
        """Lista os dados dos clientes salvos no DB"""
        total = cls.obter_total_registros("total_clientes")
        print(f"Clientes cadastrados: {total}.")

        for posicao in range(1, int(total) + 1):
            cliente = cls.obter_dado("CL_" + str(posicao))
            if cliente:
                print(f"{posicao} => {cliente}")
            else:
                print(f"{posicao} => Posição vazia")

    @classmethod
    def listar_contas(cls):
        """Lista os dados das contas salvas no DB"""
        total = cls.obter_total_registros("total_contas")
        print(f"Contas cadastrados: {total}.")

        for posicao in range(1, int(total) + 1):
            conta = cls.obter_dado("CO_" + str(posicao))
            if conta:
                print(f"{posicao} => {conta}")
            else:
                print(f"{posicao} => Posição vazia")

    @classmethod
    def salvar(cls, objeto) -> int:
        """Salva os dados no banco de dados"""
        pk = cls.obter_pk(objeto.chave)
        objeto.pk = pk
        chave = objeto.prefixo + str(pk)
        cls.salvar_dado(chave, objeto.obter_json())
        cls.atualizar_redis(tipo=type(objeto).__name__, valor=pk)
        return pk

    @classmethod
    def obter_pk(cls, chave) -> int:
        """Incrementa e retorna a PK da tabela que usa a chave como ID"""
        retries = 3
        while True:
            try:
                return cls.cache.incr(chave)
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc
                retries -= 1
                time.sleep(0.5)

    @classmethod
    def atualizar_redis(cls, **kwargs):
        """Salva metadados de cliente no banco de dados"""
        tipo = kwargs.get("tipo", "")
        total_clientes = 0
        total_contas = 0

        if tipo == Cliente.__name__:
            total_clientes = kwargs.get("valor", 0)
        elif tipo == Conta.__name__:
            total_contas = kwargs.get("valor", 0)
        else:
            raise NotImplementedError

        if total_clientes > 0:
            cls.salvar_dado("total_clientes", total_clientes)
        if total_contas > 0:
            cls.salvar_dado("total_contas", total_contas)
        cls.salvar_dado("live", 1)


# Rotinas de controle da tela
def limpar_tela():
    """Limpa a tela em diferentes sistemas operacionais"""
    os.system("cls" if os.name == "nt" else "clear")


def menu() -> str:
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


# Rotinas de manutenção do cliente e conta
def criar_cliente(clientes):
    """Cria um novo cliente, caso o CPF NÃO exista cadastrado"""
    cpf = input("Informe o CPF (somente número): ")
    cadastrado = buscar_cliente(cpf, clientes)

    if cadastrado is None:
        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascimento: ")
        endereco = input("Informe o endereço: ")

        cliente = Cliente(
            None,
            _cpf=cpf,
            _nome=nome,
            _data_nascimento=data_nascimento,
            _endereco=endereco,
        )
        if cliente.salvar(clientes):
            print("=== Cliente criado com sucesso! ===")
        else:
            print("=> Erro no banco ao salvar o cliente!")

    else:
        print("=> Já existe um cliente com esse CPF!")


def criar_conta(clientes, contas):
    """Cria uma nova conta, caso o CPF (cliente) já exista cadastrado"""
    cpf = input(MSG_0001)
    cliente = buscar_cliente(cpf, clientes)

    if cliente:
        conta = Conta(_id=None, _cliente=cliente)

        if conta.salvar(contas):
            print("=== Conta criada com sucesso! ===")
    else:
        print("=> Cliente não encontrado, impossível criar uma conta!")


def listar_contas(clientes, contas):
    """Lista todas as contas cadastradas no sistema"""

    if len(contas) == 0:
        print("== Nenhuma conta cadastrada!")
        return

    for conta in contas:
        cliente = buscar_cliente(conta.cliente.cpf, clientes)

        linha = f"""\
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero_conta}
            Titular:\t{cliente.nome}
        """
        print("=" * 50)
        print(textwrap.dedent(linha))
    print("=" * 50)


def buscar_cliente(cpf, clientes) -> Cliente | None:
    """Verifica se um CPF existe cadastrado. Caso exista, retorna a pessoa"""
    pessoa = [cliente for cliente in clientes if cliente.cpf == cpf]
    return pessoa[0] if pessoa else None


def obter_contas(cpf, contas) -> Conta | None:
    """
    Busca e retorna a primeira conta cliente. No futuro, permitir que operador selecione a conta
    """
    for conta in contas:
        if conta.cliente.cpf == cpf:
            return conta
    return None


def depositar(clientes, contas):
    """Realiza um depósito na conta do cliente"""
    cpf = input(MSG_0001)
    cliente = buscar_cliente(cpf, clientes)
    conta = obter_contas(cpf, contas)

    if cliente and conta:
        valor = float(input("Informe o valor do depósito: "))
        transacao = Deposito(valor)
        print(transacao.registrar(conta))
    else:
        print(ERR_0001)


def sacar(clientes, contas):
    """Realiza um saque na conta do cliente"""
    cpf = input(MSG_0001)
    cliente = buscar_cliente(cpf, clientes)
    conta = obter_contas(cpf, contas)

    if cliente and conta:
        valor = float(input("Informe o valor do saque: "))
        transacao = Saque(valor)
        print(transacao.registrar(conta))
    else:
        print(ERR_0001)


def emitir_extrato(clientes, contas):
    """Imprime o extrato da conta do cliente"""
    cpf = input(MSG_0001)
    cliente = buscar_cliente(cpf, clientes)
    conta = obter_contas(cpf, contas)

    if conta:
        vazio = True
        data_anterior = None
        extrato = "===================== EXTRATO ====================\n"
        extrato += f"Cliente: {cliente.nome}"

        for transacao in conta.historico.gerar_relatorio():
            vazio = False
            dia_da_transacao = datetime.strptime(
                transacao["data"], "%d-%m-%Y %H:%M:%S"
            ).date()

            if data_anterior != dia_da_transacao:
                extrato += f"\n\n{dia_da_transacao}"
            tipo = f"{transacao["tipo"]}".ljust(8)
            extrato += f"\n{tipo}:{f'R$ {transacao["valor"]:.2f}':>41}"
            data_anterior = dia_da_transacao

        if vazio:
            extrato += "\n\nNão foram realizadas movimentações"

        print(extrato)
        print(f"\nSaldo:{f'R$ {conta.saldo:.2f}':>44}")
        print("==================================================")
    else:
        print(ERR_0001)


def main():
    """Rotina principal do sistema"""
    clientes = []
    contas = []

    # Recupera dados do DB Redis, caso existam.
    PersistenciaDB.obter(clientes, Cliente.vazio())
    PersistenciaDB.obter(contas, Conta.vazio())

    while True:
        opcao = menu()
        limpar_tela()

        if opcao == "d":
            depositar(clientes, contas)

        elif opcao == "s":
            sacar(clientes, contas)

        elif opcao == "e":
            emitir_extrato(clientes, contas)

        elif opcao == "c":
            criar_cliente(clientes)

        elif opcao == "n":
            criar_conta(clientes, contas)

        elif opcao == "l":
            listar_contas(clientes, contas)

        elif opcao == "lCLI":
            # Isto faz um SELECT * from DB.Redis.Clientes e imprime na tela.
            PersistenciaDB.listar_clientes()

        elif opcao == "lCON":
            # Isto faz um SELECT * from DB.Redis.Contas e imprime na tela.
            PersistenciaDB.listar_contas()

        elif opcao == "q":
            break

        else:
            print(
                "Operação inválida, por favor selecione novamente a operação desejada."
            )


if __name__ == "__main__":
    limpar_tela()
    main()
