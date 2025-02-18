import math
import random
import sys
import os
import pickle

import neat
import pygame

# Constantes
LARGURA = 1920
ALTURA = 1080

TAMANHO_CARRO_X = 60
TAMANHO_CARRO_Y = 60

COR_DA_BORDA = (255, 255, 255, 255)  # Cor para colidir ao bater


class Carro:
    def __init__(self):
        # Carregar o Sprite do Carro e Rotacionar
        self.sprite = pygame.image.load('car.png').convert()  # Convert acelera muito
        self.sprite = pygame.transform.scale(self.sprite, (TAMANHO_CARRO_X, TAMANHO_CARRO_Y))
        self.sprite_rotacionado = self.sprite

        # Posição Inicial
        self.posicao = [830, 920]
        self.angulo = 0
        self.velocidade = 0

        self.velocidade_definida = False  # Flag para velocidade padrão mais tarde

        # Calcular o centro do carro
        self.center = [self.posicao[0] + TAMANHO_CARRO_X / 2, self.posicao[1] + TAMANHO_CARRO_Y / 2]

        self.radares = []  # Lista para Sensores / Radares
        self.radares_desenho = []  # Radares para serem desenhados

        self.vivo = True  # Booleano para verificar se o carro colidiu

        self.distancia = 0  # Distância percorrida
        self.tempo = 0  # Tempo passado

    def desenhar(self, tela):
        tela.blit(self.sprite_rotacionado, self.posicao)  # Desenhar Sprite
        self.desenhar_radar(tela)  # OPCIONAL PARA SENSORES

    def desenhar_radar(self, tela):
        # Opcionalmente Desenhar Todos os Sensores / Radares
        for radar in self.radares:
            posicao = radar[0]
            pygame.draw.line(tela, (0, 255, 0), self.center, posicao, 1)
            pygame.draw.circle(tela, (0, 255, 0), posicao, 5)

    def verificar_colisao(self, mapa_do_jogo):
        self.vivo = True
        for ponto in self.cantos:
            # Se qualquer canto tocar na cor da borda -> Colisão
            try:
                if mapa_do_jogo.get_at((int(ponto[0]), int(ponto[1]))) == COR_DA_BORDA:
                    self.vivo = False
                    break
            except IndexError:
                self.vivo = False
                break

    def verificar_radar(self, mapa_do_jogo, grau):
        comprimento = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angulo + grau))) * comprimento)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angulo + grau))) * comprimento)

        # Enquanto não atingir a COR_DA_BORDA E comprimento < 300 (apenas um máximo) -> vá mais e mais
        while comprimento < 300:
            try:
                if mapa_do_jogo.get_at((x, y)) == COR_DA_BORDA:
                    break
            except IndexError:
                break

            comprimento = comprimento + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angulo + grau))) * comprimento)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angulo + grau))) * comprimento)

        # Calcular Distância até a Borda e Adicionar à Lista de Radares
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radares.append([(x, y), dist])

    def atualizar(self, mapa_do_jogo):
        # Definir a Velocidade para 20 pela Primeira Vez
        if not self.velocidade_definida:
            self.velocidade = 20
            self.velocidade_definida = True

        # Obter o Sprite Rotacionado e Mover na Direção X Correta
        self.sprite_rotacionado = self.rotacionar_center(self.sprite, self.angulo)
        self.posicao[0] += math.cos(math.radians(360 - self.angulo)) * self.velocidade
        self.posicao[0] = max(self.posicao[0], 20)
        self.posicao[0] = min(self.posicao[0], LARGURA - 120)

        # Aumentar Distância e Tempo
        self.distancia += self.velocidade
        self.tempo += 1

        # O Mesmo para a Posição Y
        self.posicao[1] += math.sin(math.radians(360 - self.angulo)) * self.velocidade
        self.posicao[1] = max(self.posicao[1], 20)
        self.posicao[1] = min(self.posicao[1], ALTURA - 120)  # Corrigido: LARGURA -> ALTURA

        # Calcular Novo Centro
        self.center = [int(self.posicao[0]) + TAMANHO_CARRO_X / 2, int(self.posicao[1]) + TAMANHO_CARRO_Y / 2]

        # Calcular Quatro Cantos
        comprimento = 0.5 * TAMANHO_CARRO_X
        canto_superior_esquerdo = [self.center[0] + math.cos(math.radians(360 - (self.angulo + 30))) * comprimento,
                                   self.center[1] + math.sin(math.radians(360 - (self.angulo + 30))) * comprimento]
        canto_superior_direito = [self.center[0] + math.cos(math.radians(360 - (self.angulo + 150))) * comprimento,
                                  self.center[1] + math.sin(math.radians(360 - (self.angulo + 150))) * comprimento]
        canto_inferior_esquerdo = [self.center[0] + math.cos(math.radians(360 - (self.angulo + 210))) * comprimento,
                                   self.center[1] + math.sin(math.radians(360 - (self.angulo + 210))) * comprimento]
        canto_inferior_direito = [self.center[0] + math.cos(math.radians(360 - (self.angulo + 330))) * comprimento,
                                  self.center[1] + math.sin(math.radians(360 - (self.angulo + 330))) * comprimento]
        self.cantos = [canto_superior_esquerdo, canto_superior_direito, canto_inferior_esquerdo,
                         canto_inferior_direito]

        # Verificar Colisões e Limpar Radares
        self.verificar_colisao(mapa_do_jogo)
        self.radares.clear()

        # De -90 a 120 com Passo de 45 Verificar Radar
        for d in range(-90, 120, 45):
            self.verificar_radar(mapa_do_jogo, d)

    def obter_dados(self):
        # Obter Distâncias até a Borda
        radares = self.radares
        valores_retorno = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radares):
            valores_retorno[i] = int(radar[1] / 30)

        return valores_retorno

    def esta_vivo(self):
        # Função Básica de Verificação de Vida
        return self.vivo

    def obter_recompensa(self):
        # Calcular Recompensa
        return self.distancia / (TAMANHO_CARRO_X / 2)

    def rotacionar_center(self, imagem, angulo):
        # Rotacionar o Retângulo
        retangulo = imagem.get_rect()
        imagem_rotacionada = pygame.transform.rotate(imagem, angulo)
        retangulo_rotacionado = retangulo.copy()
        retangulo_rotacionado.center = imagem_rotacionada.get_rect().center
        imagem_rotacionada = imagem_rotacionada.subsurface(retangulo_rotacionado).copy()
        return imagem_rotacionada

def load_map():
    return pygame.image.load('map.png').convert()