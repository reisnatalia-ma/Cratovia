import csv
import os 
import posts.csv

'''caminho dos arquivos'''

caminho_comentarios = "dados/comentarios.csv"
caminho_avaliações = "dados/avaliações"

'''comentario'''

def adicionar_comentario(post_id, autor, comentario)
  with open(caminho_comentarios, mode='r', encoding='utf-8') as f:
    linhas = list(csv.reader(f))
    novo_id = len(linhas)

  with open(caminho_comentarios, mode='a', newline '', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([novo_id, post_id, autor, comentario])

def listar_comentarios(post_id):
  comentarios = []

  with open(caminho_comentarios, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for linha in reader:
      if linha["post_id"] == str(post_id):
        comentarios.append(linha)
  
  return comentarios

'''avaliações'''

def avaliar_post(post_id, usuario, veridico):

  '''impedir usuario de avaliar duas vezes'''
  with open(caminho_comentarios, mode='a', newline '', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for linha in reader:
    if linha["post_id"] == srt(post_id) and linha["usuario"] == usuario:
      print("Usuário já avaliou este post.")
      return
   
  with open(caminho_comentarios, mode='r', encoding='utf-8') as f:
    linhas = list(csv.reader(f))
    novo_id = len(linhas)

  with open(caminho_comentarios, mode='r', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([novo_id, post_id, usuario, veridico])


def contar_avaliacoes(post_id):
  positivos = 0
  negativos = 0 

  with open(caminho_comentarios, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for linha in reader:
      if linha["post_id"] == str(post_id):
        positivo += 1
      else:
        negativos += 1
        
  return positivos, negativos
