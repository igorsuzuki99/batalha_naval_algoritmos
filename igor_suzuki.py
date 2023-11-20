# Projeto Batalha Naval em Python
import sys

# recebe o nome do arquivo, lê as linhas e extrai informações sobre as posições das embarcações e torpedos
def ler_arquivo(nome_arquivo):
    with open(nome_arquivo) as arquivo:
        torpedos = []
        posicoes_embarcacoes = {}
        for linha in arquivo:
            linha = linha.rstrip()
            if linha[0] in "1234":
                tipo_embarcacao, coordenadas = linha.split(';')
                posicoes_embarcacoes[tipo_embarcacao] = coordenadas.split('|')
            elif linha[0] == 'T':
                torpedos = linha.split(';')[1].split('|')
    return {'posicoes_embarcacoes': posicoes_embarcacoes, 'torpedos': torpedos}

#  verifica se uma posição (linha e coluna) está dentro dos limites do tabuleiro
def validar_posicao(linha, coluna, id_jogador):
    return 0 <= linha <= 15 and 0 <= coluna <= 15

# escreve o resultado no arquivo de saída
def escrever_resultado(resultado):
    with open('resultado.txt', 'w') as arquivo:
        arquivo.write(resultado)
    sys.exit()

# valida se o número de partes para cada tipo de embarcação e torpedos está de acordo com as regras do jogo
def validar_numero_partes(jogada, id_jogador):
    tamanho_esperado = {'1': 5, '2': 2, '3': 10, '4': 5, 'T': 25}

    # verifica se o número de partes corresponde ao esperado para cada tipo de embarcação e torpedos
    def verificar_partes(tipo, coordenadas):
        if len(coordenadas) != tamanho_esperado[tipo]:
            escrever_resultado(f"J{id_jogador} ERROR_NR_PARTS_VALIDATION")

    for tipo, coordenadas in jogada['posicoes_embarcacoes'].items():
        verificar_partes(tipo, coordenadas)

    verificar_partes('T', jogada['torpedos'])

# valida se as posições dos torpedos estão dentro dos limites do tabuleiro
def validar_torpedos(torpedos, id_jogador):
    letras = "ABCDEFGHIJLMNOP"

    # converte a posição do torpedo para coordenadas (linha, coluna) e verifica se está dentro dos limites do tabuleiro
    def validar_posicao_torpedo(torpedo):
        linha, coluna = letras.find(torpedo[0]), int(torpedo[1:])
        if not validar_posicao(linha, coluna, id_jogador):
            escrever_resultado(f"J{id_jogador} ERROR_POSITION_NONEXISTENT_VALIDATION")

    for torpedo in torpedos:
        validar_posicao_torpedo(torpedo)

# verifica se as posições das embarcações são válidas e gera um dicionário de posições ocupadas por embarcações
def verificar_e_gerar_posicoes(posicoes_embarcacoes, id_jogador):
    posicoes_ocupadas = {}
    letras = "ABCDEFGHIJLMNOP"
    tamanhos_embarcacoes = {'1': 4, '2': 5, '3': 1, '4': 2}
    id_embarcacao = 0

    # gera as coordenadas das partes de uma embarcação com base na posição inicial, orientação e tamanho
    def obter_coordenadas(linha, coluna, orientacao_vertical, tamanho_embarcacao):
        coordenadas = []
        for i in range(tamanho_embarcacao):
            nova_linha = linha + i if orientacao_vertical else linha
            nova_coluna = coluna + i if not orientacao_vertical else coluna
            coordenadas.append((nova_linha, nova_coluna))
        return coordenadas

    for tipo_embarcacao, coordenadas in posicoes_embarcacoes.items():
        tamanho_embarcacao = tamanhos_embarcacoes[tipo_embarcacao]
        for coordenada in coordenadas:
            orientacao_vertical = coordenada[-1] == 'V'
            coordenada = coordenada[:-1] if coordenada[-1] in 'HV' else coordenada
            linha, coluna = letras.find(coordenada[0]), int(coordenada[1:])

            # se a posição inicial não estiver dentro dos limites, gera o erro de position_nonexistent
            if not validar_posicao(linha, coluna, id_jogador):
                escrever_resultado(f"J{id_jogador} ERROR_POSITION_NONEXISTENT_VALIDATION")

            novas_posicoes = obter_coordenadas(linha, coluna, orientacao_vertical, tamanho_embarcacao)

            for nova_linha, nova_coluna in novas_posicoes:

                # verifica se há sobreposição de embarcações
                nova_posicao = f"{nova_linha};{nova_coluna}"
                if nova_posicao in posicoes_ocupadas:
                    escrever_resultado(f"J{id_jogador} ERROR_OVERWRITE_PIECES_VALIDATION")
                posicoes_ocupadas[nova_posicao] = id_embarcacao

            id_embarcacao += 1

    return posicoes_ocupadas

# calcula os resultados do jogador com base nos torpedos disparados e nas posições ocupadas pelas embarcações
def calcular_resultados(torpedos, posicoes_ocupadas, id_jogador):
    pontos = 0
    ids_acertados = set()
    pontos_acerto = 3
    pontos_afundamento = 2
    total_alvos = 22

    for torpedo in torpedos:
        letras = "ABCDEFGHIJLMNOP"
        linha = letras.find(torpedo[0])
        coluna = int(torpedo[1:])
        posicao = f"{linha};{coluna}"

        # se o torpedo atingir uma embarcação jogador recebe 3 pontos
        if posicao in posicoes_ocupadas:
            id_embarcacao = posicoes_ocupadas.pop(posicao)
            pontos += pontos_acerto
            ids_acertados.add(id_embarcacao)

            # se a embarcação for totalmente atingida, jogador recebe 5 pontos (3+2)
            if id_embarcacao not in posicoes_ocupadas.values():
                pontos += pontos_afundamento

    acertos = len(ids_acertados)
    erros = total_alvos - acertos

    return {'pontos': pontos, 'alvos': erros, 'acertos': acertos}

# lê o arquivo do jogador, valida as informações e retorna a jogada como um dicionário
def ler_jogada_e_validar(arquivo, id_jogador):
    jogada = ler_arquivo(arquivo)
    validar_numero_partes(jogada, id_jogador)
    validar_torpedos(jogada['torpedos'], id_jogador)
    return jogada

# escreve os resultados dos jogadores no arquivo resultado.txt
def escrever_resultados(resultado_jogador1, resultado_jogador2):
    template = "{}AA {}AE {}PT"

    if resultado_jogador1['pontos'] == resultado_jogador2['pontos']:
        escrever_resultado("J1 " + template.format(resultado_jogador1['acertos'], resultado_jogador1['alvos'], resultado_jogador1['pontos']) +
                            '\n' + "J2 " + template.format(resultado_jogador2['acertos'], resultado_jogador2['alvos'], resultado_jogador2['pontos']))
    elif resultado_jogador1['pontos'] > resultado_jogador2['pontos']:
        escrever_resultado("J1 " + template.format(resultado_jogador1['acertos'], resultado_jogador1['alvos'], resultado_jogador1['pontos']))
    else:
        escrever_resultado("J2 " + template.format(resultado_jogador2['acertos'], resultado_jogador2['alvos'], resultado_jogador2['pontos']))

# função principal p/ ler, validar, calcular resultados e escrever os resultados dos jogadores
def main():
    jogador1, jogador2 = ler_jogada_e_validar('jogador1.txt', 1), ler_jogada_e_validar('jogador2.txt', 2)

    posicoes_ocupadas_jogador1 = verificar_e_gerar_posicoes(jogador1['posicoes_embarcacoes'], 1)
    posicoes_ocupadas_jogador2 = verificar_e_gerar_posicoes(jogador2['posicoes_embarcacoes'], 2)

    resultado_jogador1 = calcular_resultados(jogador1['torpedos'], posicoes_ocupadas_jogador2, 1)
    resultado_jogador2 = calcular_resultados(jogador2['torpedos'], posicoes_ocupadas_jogador1, 2)

    escrever_resultados(resultado_jogador1, resultado_jogador2)

# execução do programa
main()