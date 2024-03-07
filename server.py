import asyncio
import json

# Classe représentant un joueur
class Player:
  def __init__(self, x, y, name, color):
    self.x = x
    self.y = y
    self.name = name
    self.color = color

# Liste des joueurs connectés
players = []

async def handle_connection(reader, writer):
  # Création d'un joueur pour le nouveau client
  player = Player(0, 0, "", "red")
  players.append(player)

  try:
    while True:
      # Réception des données envoyées par le client
      data = await reader.read(1024)
      if not data:
        break
      data = data.decode()
      data = json.loads(data)

      # Traitement des données reçues (par exemple, mise à jour de la position du joueur)
      if 'x' in data and 'y' in data :
        player.x = data['x']
        player.y = data['y']
      if 'name' in data and 'color' in data :
        player.name = data['name']
        player.color = data['color']

      # Envoi de l'état du jeu aux clients
      state = {'players': []}
      for p in players:
        state['players'].append({'name': p.name, 'x': p.x, 'y': p.y, 'color': p.color})
      state = json.dumps(state)
      state = state.encode()
      writer.write(state)
      await writer.drain()
  finally:
    # Suppression du joueur de la liste des joueurs connectés
    players.remove(player)

    # Fermeture de la connexion avec le client
    writer.close()

async def main():
  # Création de la socket
  server = await asyncio.start_server(handle_connection, 'localhost', 12345)

  # Attente de connexions des clients
  await server.serve_forever()

# Exécution de la boucle d'événements
asyncio.run(main())
