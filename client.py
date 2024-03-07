import asyncio
import json
import pygame

def collision(rect1, rect2):
  # Vecteurs de projection sur les axes x et y
  axes = [(1, 0), (0, 1)]
  value = [0,0,0,0]
  
  # Pour chaque axe, on calcule les projections des deux carrés
  for axis in axes:
    # Projection du premier carré sur l'axe
    proj1 = project(rect1, axis)
    # Projection du second carré sur l'axe
    proj2 = project(rect2, axis)
    # Si les projections ne se chevauchent pas, alors les carrés ne se chevauchent pas non plus
    if not overlap(proj1, proj2):
      return value

  # Si aucun des axes ne sépare les carrés, alors ils se chevauchent
  # On calcule alors la direction de la collision en comparant les positions des deux carrés
  if rect1.x+rect1.width >= rect2.x and rect1.x+rect1.width <= rect2.x+rect2.width and ((rect1.y > rect2.y and rect1.y < rect2.y+rect2.height) or (rect1.y+rect1.height > rect2.y and rect1.y+rect1.height < rect2.y+rect2.height)):
    # Collision à droite
    value[0] = 1
  if rect1.x <= rect2.x+rect2.width and rect1.x >= rect2.x and ((rect1.y > rect2.y and rect1.y < rect2.y+rect2.height) or (rect1.y+rect1.height > rect2.y and rect1.y+rect1.height < rect2.y+rect2.height)):
    # Collision à gauche
    value[1] = 1
  if rect1.y+rect1.height >= rect2.y and rect1.y+rect1.height <= rect2.y+rect2.height and ((rect1.x > rect2.x and rect1.x < rect2.x+rect2.width) or (rect1.x+rect1.width > rect2.x and rect1.x+rect1.width < rect2.x+rect2.width)):
    # Collision en bas
    value[3] = 1
  if rect1.y <= rect2.y+rect2.height and rect1.y >= rect2.y and ((rect1.x > rect2.x and rect1.x < rect2.x+rect2.width) or (rect1.x+rect1.width > rect2.x and rect1.x+rect1.width < rect2.x+rect2.width)):
    # Collision en haut
    value[2] = 1

  if rect1.y == rect2.y and rect1.x+rect1.width >= rect2.x and rect1.x+rect1.width <= rect2.x+rect2.width:
    # Collision à droite
    value[0] = 1
  if rect1.y == rect2.y and rect1.x <= rect2.x+rect2.width and rect1.x >= rect2.x:
    # Collision à gauche
    value[1] = 1
  if rect1.x == rect2.x and rect1.y+rect1.height >= rect2.y and rect1.y+rect1.height <= rect2.y+rect2.height:
    # Collision en bas
    value[3] = 1
  if rect1.x == rect2.x and rect1.y <= rect2.y+rect2.height and rect1.y >= rect2.y:
    # Collision en bas
    value[2] = 1

  return value

def project(rect, axis):
  # Calcul des points du carré
  points = [
    (rect.x, rect.y),
    (rect.x + rect.width, rect.y),
    (rect.x + rect.width, rect.y + rect.height),
    (rect.x, rect.y + rect.height)
  ]

  # Calcul des projections des points sur l'axe
  projections = [dot(point, axis) for point in points]

  # Retourne le minimum et le maximum de ces projections
  return (min(projections), max(projections))

def overlap(proj1, proj2):
  # Si les projections se chevauchent, alors les formes de collision se chevauchent également
  return proj1[0] <= proj2[1] and proj2[0] <= proj1[1]

def dot(point, axis):
  # Calcul de la projection du point sur l'axe
  projection = point[0] * axis[0] + point[1] * axis[1]
  return projection

async def main():
  # Initialisation de pygame
  pygame.init()

  # Création de la fenêtre de jeu
  screen = pygame.display.set_mode((640, 480))

  #nom (agissant comme un id)
  player_name = input("Entrez votre nom : ")
  
  # Couleur du joueur
  player_color = input("Entrez ta couleur (red, green, yellow) : ")

  # Taille du carré représentant le joueur
  player_size = 50

  # Vitesse de déplacement du joueur (en pixels par frame)
  player_speed = 1

  # Direction du déplacement du joueur (0: droite, 1: gauche, 2: haut, 3: bas)
  player_direction = [0, 0, 0, 0]

  # Coordonnées du joueur (reçues du serveur)
  player_x = 0
  player_y = 0

  # Position précédente du personnage (utilisée pour l'interpolation)
  prev_player_x = 0
  prev_player_y = 0

  # Coefficient d'interpolation (entre 0 et 1)
  interp = 0.5

  # hitbox (0: droite, 1: gauche, 2: haut, 3: bas)
  hitbox = [0, 0, 0, 0]

  # Création de la socket
  reader, writer = await asyncio.open_connection('localhost', 12345)

  # Boucle de jeu principale
  running = True
  while running:
    # Traitement des événements
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
          player_direction[0] = 1
        elif event.key == pygame.K_LEFT:
          player_direction[1] = 1
        elif event.key == pygame.K_UP:
          player_direction[2] = 1
        elif event.key == pygame.K_DOWN:
          player_direction[3] = 1
      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT:
          player_direction[0] = 0
        elif event.key == pygame.K_LEFT:
          player_direction[1] = 0
        elif event.key == pygame.K_UP:
          player_direction[2] = 0
        elif event.key == pygame.K_DOWN:
          player_direction[3] = 0

    # Mise à jour de la position précédente du personnage
    prev_player_x = player_x
    prev_player_y = player_y
    
    # Mise à jour de la position actuelle du personnage
    if player_direction[0] == 1 and not hitbox[0]:
      player_x += player_speed
    if player_direction[1] == 1 and not hitbox[1]:
      player_x -= player_speed
    if player_direction[2] == 1 and not hitbox[2]:
      player_y -= player_speed
    if player_direction[3] == 1 and not hitbox[3]:
      player_y += player_speed

    # Interpolation de la position du personnage
    player_x = prev_player_x + (player_x - prev_player_x) * interp
    player_y = prev_player_y + (player_y - prev_player_y) * interp

    # Envoi de la nouvelle position du joueur au serveur
    data = {'name': player_name, 'x': player_x, 'y': player_y, 'color': player_color}
    data = json.dumps(data)
    data = data.encode()
    writer.write(data)
    await writer.drain()

    # Réception de l'état du jeu du serveur
    data = await reader.read(1024)
    data = data.decode()
    data = json.loads(data)

    # Mise à jour de l'état du jeu (par exemple, positions des autres joueurs)
    players = data['players']

    # Effacement de l'écran
    screen.fill((0, 0, 0))
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    hitbox = [0, 0, 0, 0]
    # Dessin des joueurs
    for p in players:
      if p['name'] != player_name:
        p_rect = pygame.Rect(p['x'], p['y'], player_size, player_size)
        is_hitting = collision(player_rect, p_rect)
        if is_hitting[0]:
          hitbox[0] = 1
        if is_hitting[1]:
          hitbox[1] = 1
        if is_hitting[2]:
          hitbox[2] = 1
        if is_hitting[3]:
          hitbox[3] = 1
      pygame.draw.rect(screen, p['color'], (p['x'], p['y'], player_size, player_size))

    # Mise à jour de l'affichage
    pygame.display.flip()

  # Fermeture de la connexion
  writer.close()

# Exécution de la boucle d'événements
asyncio.run(main())

# Fermeture de pygame
pygame.quit()

