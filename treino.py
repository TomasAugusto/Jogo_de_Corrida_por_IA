import neat
import pygame
import sys
from main import Carro, LARGURA, ALTURA, load_map
import pickle

geracao_atual = 0  # Contador de gerações

def rodar_simulacao(genomas, config):
    # Coleções Vazias para Redes e Carros
    redes = []
    carros = []

    # Inicializar PyGame e o Display
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)

    # Para Todos os Genomas Passados Criar uma Nova Rede Neural
    for i, g in genomas:
        rede = neat.nn.FeedForwardNetwork.create(g, config)
        redes.append(rede)
        g.fitness = 0
        carros.append(Carro())

    # Configurações do Relógio e Carregamento do Mapa
    relogio = pygame.time.Clock()
    fonte_geracao = pygame.font.SysFont("Arial", 30)
    fonte_vivo = pygame.font.SysFont("Arial", 20)
    mapa_do_jogo = load_map()

    global geracao_atual
    geracao_atual += 1

    # Contador Simples para Limitar o Tempo
    contador = 0

    while True:
        # Sair no Evento de Quit
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Para Cada Carro Obter a Ação que Ele Toma
        for i, carro in enumerate(carros):
            saida = redes[i].activate(carro.obter_dados())
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

        # Verificar se o Carro Ainda Está Vivo
        ainda_vivos = 0
        for i, carro in enumerate(carros):
            if carro.esta_vivo():
                ainda_vivos += 1
                carro.atualizar(mapa_do_jogo)
                genomas[i][1].fitness += carro.obter_recompensa()

        if ainda_vivos == 0:
            break

        contador += 1
        if contador == 30 * 40:  # Parar após cerca de 20 segundos
            break

        # Desenhar Mapa e Todos os Carros que Estão Vivos
        tela.blit(mapa_do_jogo, (0, 0))
        for carro in carros:
            if carro.esta_vivo():
                carro.desenhar(tela)

        # Exibir Informações
        texto = fonte_geracao.render("Geração: " + str(geracao_atual), True, (0, 0, 0))
        retangulo_texto = texto.get_rect()
        retangulo_texto.center = (900, 450)
        tela.blit(texto, retangulo_texto)

        texto = fonte_vivo.render("Ainda Vivos: " + str(ainda_vivos), True, (0, 0, 0))
        retangulo_texto = texto.get_rect()
        retangulo_texto.center = (900, 490)
        tela.blit(texto, retangulo_texto)

        pygame.display.flip()
        relogio.tick(60)  # 60 FPS

    # Identificar e Salvar o Melhor Piloto
    melhor_fitness = -1
    melhor_genoma = None
    for i, carro in enumerate(carros):
        if genomas[i][1].fitness > melhor_fitness:
            melhor_fitness = genomas[i][1].fitness
            melhor_genoma = genomas[i][1]

    if melhor_genoma:
        with open("melhor_piloto.pkl", "wb") as f:
            pickle.dump(melhor_genoma, f)


if __name__ == "__main__":
    # Carregar Configuração
    caminho_config = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    # Rodar a simulação para treinar a IA
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    estatisticas = neat.StatisticsReporter()
    populacao.add_reporter(estatisticas)
    populacao.run(rodar_simulacao, 10)

    print("Treinamento concluído. O melhor piloto foi salvo em 'melhor_piloto.pkl'")