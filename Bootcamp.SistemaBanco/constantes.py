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
Constantes para o sistema Bancário com Python.

    Parameters:
        Nenhum

    Returns:
        Nenhum.
"""
from typing import Final

AGENCIA: Final[str] = "0001"
QTDE_MAXIMA_SAQUES: Final[int] = 3
VALOR_MAXIMO_POR_SAQUE: Final[float] = 500.0


class Erro:  # pylint: disable-msg=R0903
    """Mensagens de erro"""

    CLI_NAO_ENCONTRADO: Final[str] = "==> Cliente não encontrado ou não possui conta!"
    OPE_VALOR_INVALIDO: Final[str] = (
        "==> Operação falhou! O valor informado é inválido!"
    )


class Aviso:  # pylint: disable-msg=R0903
    """Textos de informação"""

    MSG_INFORME_CPF: Final[str] = "Informe o CPF do cliente: "


MENU_PRINCIPAL: Final[
    str
] = """\n
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
