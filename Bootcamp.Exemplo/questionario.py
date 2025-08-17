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
# Programa para testar uma funcionalidade do Python
# More info at https://github.com/portfolio-2025br/bootcamp-python

"""
Documentar a resposta correta para a seguite pergunta do questionário:

Dado o código:
  from datetime import datetime
  date_string = "2023-05-01"
  date_obj = datetime.strptime(date_string, "%Y-%d-%m")

    Parameters:
        Nenhum

    Returns:
        Nenhum
"""

from datetime import datetime

DATE_STRING = "2023-05-01"
date_obj = datetime.strptime(DATE_STRING, "%Y-%d-%m")

print(type(date_obj))
print(date_obj.strftime("%B %d %Y"))
