#!/usr/bin/env python3

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
