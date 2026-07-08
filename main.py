import os
import sys
from memoria import registradores, memoria_ram
from instrucoes import executar_instrucao

def hex_para_indice(hex_str):
    """ Converte uma string hexadecimal para um número inteiro. """
    hex_str = hex_str.strip()
    return int(hex_str, 16)

def indice_para_hex(indice):
    """ Converte um número inteiro de volta para string hexadecimal. """
    if isinstance(indice, str):
        return indice
    return f"0x{indice:02X}"

def ler_entrada(caminho):
    """ Lê o arquivo de texto linha por linha e devolve uma lista de strings. """
    if not os.path.exists(caminho):
        print(f"Arquivo de testes '{caminho}' não foi encontrado.")
        return None
    linhas = []
    with open(caminho) as arq:
        for linha in arq:
            linhas.append(linha)
    return linhas

def interpretar_entrada(caminho):
    """
    Pega as linhas do arquivo e divide nas 3 seções:
    01. Dados
    02. Endereço inicial
    03. Instruções
    """

    lista_linhas = ler_entrada(caminho)
    if not lista_linhas:
        return None

    secoes = {'.DADOS': 0, '.INICIO': 1, '.CODIGO': 2}
    dados = []
    endereco_inicial = None
    instrucoes = []
    secao_atual = 0

    for linha in lista_linhas:
        linha = linha.strip()

        # Controla aonde deve ser armazenado
        if linha.upper() in secoes:
            secao_atual = secoes[linha.upper()]
            continue

        if not linha:
            continue
        if linha.startswith('#'):
            # Ignora comentários puros
            continue

        if secao_atual == 0:
            # Lendo os dados
            try:
                dados.append(int(linha, 0))
            except ValueError:
                print(f"Erro ao interpretar dado: {linha}")
        elif secao_atual == 1:
            # Lendo o endereço inicial
            try:
                endereco_inicial = hex_para_indice(linha)
            except ValueError:
                print(f"Erro ao interpretar endereço: {linha}")
        elif secao_atual == 2:
            # Lendo as instruções
            instrucoes.append(linha)

    return {
        'dados': dados,
        'endereco_inicial': endereco_inicial,
        'instrucoes': instrucoes
    }

def printar_estado():
    ''' Imprime o estado dos regs e da memória para debug '''
    mbr = registradores['MBR']
    mbr_str = indice_para_hex(mbr) if isinstance(mbr, int) else str(mbr)

    print(f"\nPC: {indice_para_hex(registradores['PC'])} | MAR: {indice_para_hex(registradores['MAR'])}")
    print(f"IR: {registradores['IR']} | MBR: {mbr_str}")
    print(f"A: {registradores['A']} | B: {registradores['B']}")
    print(f"AC: {registradores['AC']}" f" | M: {registradores['M']} | R: {registradores['R']}")
    print(f"C: {registradores['C']} | N: {registradores['N']} | Z: {registradores['Z']}")
    print("\n" * 2)

def inicializar_memoria_selection_sort(memoria, programa_dados):
    """ Inicializa a memória especificamente para o mapeamento do Selection Sort. """
    for i, valor in enumerate(programa_dados):
        memoria[0x100 + i] = valor
    print("Memória inicializada para o Selection Sort (Base 0x100).")

def inicializar_memoria_padrao(memoria, programa_dados, endereco_base=0x00):
    """ Inicializa a memória genericamente para outros algoritmos, dentro do limite de 0xFF. """
    for i, valor in enumerate(programa_dados):
        memoria[endereco_base + i] = valor
    print()
    print(f"Memória inicializada padrão a partir de {hex(endereco_base)}.")

def main():
    if len(sys.argv) < 2:  # Verifica o tamanho da lista de argumentos
        print("Uso correto: python main.py [nome_do_arquivo.txt]")
        return
    arquivo = sys.argv[1]

    # Transforma o arquivo de texto em dados, endereço inicial e comandos
    programa = interpretar_entrada(arquivo)

    if programa is None:
        return

    is_selection_sort = "selection_sort" in arquivo.lower()
    is_fibonacci = "fibonacci" in arquivo.lower()

    inicializar_memoria_padrao(memoria_ram, programa['dados'], endereco_base=0x00)

    # Guarda as instruções na RAM de forma sequencial
    endereco_instrucao = programa['endereco_inicial']
    for instrucao in programa['instrucoes']:
        memoria_ram[endereco_instrucao] = instrucao
        endereco_instrucao += 1

    # Aponta o PC para a primeira instrução
    registradores['PC'] = programa['endereco_inicial']

    print("Estado Inicial:")
    printar_estado()

    flag = True
    while flag:
        if not (0 <= registradores['PC'] <= 0xFF):        # PC saiu da RAM
            print("Fim do programa (PC fora da memoria).")
            flag = False
            continue

        # CICLO DE BUSCA

        # MAR <- PC
        registradores['MAR'] = registradores['PC']

        # Captura o conteúdo bruto da memória primeiro
        conteudo_ram = memoria_ram[registradores['MAR']]

        if isinstance(conteudo_ram, str) and conteudo_ram.strip().upper() == 'HALT':
            print("Fim do programa.")
            flag = False
            continue

        # Verifica a condição de paragem antes de tratar como instrução
        if conteudo_ram == 0 or conteudo_ram == "" or conteudo_ram is None:
            print("Fim do programa.")
            flag = False
            continue

        # 2. MBR <- MEM[MAR]
        registradores['MBR'] = memoria_ram[registradores['MAR']]

        # 3. IR <- MBR
        registradores['IR'] = registradores['MBR']

        # 4. PC <- PC + 1
        registradores['PC'] += 1

        instrucao_atual = registradores['IR']
        print(f"Instrução a ser executada: {instrucao_atual}")

        # CICLO DE EXECUÇÃO

        # 5. Executar instrução
        executar_instrucao(instrucao_atual)

        printar_estado()
        input("Pressione ENTER para continuar...")

    # Se for o Selection Sort, imprime como ficou o vetor ordenado
    if is_selection_sort:
      print("\n--- Resultado do Vetor na Memória (0x10 - 0x14) ---")
      for i in range(0x10, 0x15):
          print(f"MEM[{hex(i)}] = {memoria_ram[i]}")
      print()

    # Se for o Fibonacci, imprime como ficou o vetor
    if is_fibonacci:
      print("\n--- Resultado do Vetor na Memória (0x20 - 0x29) ---")
      for i in range(0x20, 0x2a):
          print(f"MEM[{hex(i)}] = {memoria_ram[i]}")
      print()

if __name__ == "__main__":
    main()
