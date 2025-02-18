import neat
import pygame
import sys
import pickle 
from main import Carro, LARGURA, ALTURA, load_map
import math

def jogar_com_melhor_piloto(config, num_voltas=3):
    # Carregar o genoma do melhor piloto
    try:
        with open("melhor_piloto.pkl", "rb") as f:
            melhor_genoma = pickle.load(f)
    except FileNotFoundError:
        print("Arquivo 'melhor_piloto.pkl' não encontrado. Certifique-se de que a simulação foi executada primeiro.")
        return

    # Criar a rede neural a partir do genoma
    rede = neat.nn.FeedForwardNetwork.create(melhor_genoma, config)

    # Inicializar PyGame e o Display
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
    pygame.display.set_caption("Melhor Piloto")  # Define o título da janela

    # Criar o carro
    carro = Carro()

    # Configurações do Relógio e Carregamento do Mapa
    relogio = pygame.time.Clock()
    mapa_do_jogo = load_map()
    fonte_vivo = pygame.font.SysFont("Arial", 20)  # Fonte para o texto "Melhor Piloto"

    voltas_completadas = 0
    ponto_de_inicio = (830, 920)  # Ponto inicial do carro
    distancia_ultima_volta = 0  # Distância percorrida na última volta
    distancia_para_considerar_volta = 2500  # Ajuste este valor com base no comprimento da pista
    distancia_maxima_ao_inicio = 100  # Ajuste este valor para tolerância da linha de chegada

    # Verifica a distância inicial e define em_volta de acordo
    distancia_inicial = math.sqrt(
        (carro.posicao[0] - ponto_de_inicio[0]) ** 2 + (carro.posicao[1] - ponto_de_inicio[1]) ** 2)
    em_volta = distancia_inicial < distancia_maxima_ao_inicio

    while voltas_completadas < num_voltas:
        # Sair no Evento de Quit
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Obter a ação do melhor piloto
        saida = rede.activate(carro.obter_dados())
        escolha = saida.index(max(saida))
        if escolha == 0:
            carro.angulo += 10  # Esquerda
        elif escolha == 1:
            carro.angulo -= 10  # Direita
        elif escolha == 2:
            if carro.velocidade - 2 >= 12:
                carro.velocidade -= 2  # Desacelerar
        else:
            carro.velocidade += 2  # Acelerar

        # Atualizar o carro
        carro.atualizar(mapa_do_jogo)

        # Verificar se completou uma volta (aproximação ao ponto inicial)
        distancia_ao_inicio = math.sqrt(
            (carro.posicao[0] - ponto_de_inicio[0]) ** 2 + (carro.posicao[1] - ponto_de_inicio[1]) ** 2)

        # Lógica do gatilho da volta
        if distancia_ao_inicio < distancia_maxima_ao_inicio:
            if not em_volta:  # Se não estiver em uma volta
                voltas_completadas += 1
                distancia_ultima_volta = carro.distancia
                print(f"Volta {voltas_completadas} completada!")
                em_volta = True  # Ativa o gatilho
        else:
            em_volta = False  # Desativa o gatilho quando se afasta da linha de chegada

        # Desenhar Mapa e o Carro
        tela.blit(mapa_do_jogo, (0, 0))
        carro.desenhar(tela)

        # Desenhar texto "Melhor Piloto" e número de voltas
        texto_piloto = fonte_vivo.render("Melhor Piloto", True, (0, 0, 0))  # Cor preta
        retangulo_texto_piloto = texto_piloto.get_rect()
        retangulo_texto_piloto.center = (900, 490)  # Centralizar verticalmente como "Ainda Vivos"
        tela.blit(texto_piloto, retangulo_texto_piloto)

        texto_voltas = fonte_vivo.render(f"Voltas: {voltas_completadas}/{num_voltas}", True, (0, 0, 0))
        retangulo_texto_voltas = texto_voltas.get_rect()
        retangulo_texto_voltas.center = (900, 530)  # Posicionar abaixo de "Melhor Piloto"
        tela.blit(texto_voltas, retangulo_texto_voltas)

        pygame.display.flip()
        relogio.tick(60)  # 60 FPS

    # Finalizar o Pygame
    pygame.quit()
    print("Simulação do melhor piloto finalizada!")


if __name__ == "__main__":
    # Carregar Configuração
    caminho_config = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    # Jogar com o melhor piloto
    jogar_com_melhor_piloto(config, num_voltas=3)