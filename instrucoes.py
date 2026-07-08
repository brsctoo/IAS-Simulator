from memoria import registradores, memoria_ram
import sys

# FLAGS
def atualizar_flags(valor):
    registradores['Z'] = 1 if valor == 0 else 0
    registradores['N'] = 1 if valor < 0 else 0

# HELPERS
def endereco_para_inteiro(endereco):
    if isinstance(endereco, int):
        return endereco

    # Transforma M(x) em x
    endereco = endereco.strip().replace('M(', '').replace(')', '').replace(',' , '')
    return int(endereco, 0)

def reg_valido(nome):
    """Verifica se o nome é um registrador existente."""
    return nome.upper() in registradores

def parse_reg_e_endereco(partes):
    """
    Recebe as partes da instrução sem o mnemônico e retorna (reg, endereco).
    Se vier com registrador explícito: ['A,', 'M(0x05)'] -> ('A', 'M(0x05)')
    Se vier sem registrador: ['M(0x05)'] -> ('AC', 'M(0x05)')
    """
    if len(partes) == 2:
        reg = partes[0].replace(',', '').upper()
        endereco = partes[1].replace(',', '')
        return reg, endereco
    else:
        return 'AC', partes[0].replace(',', '')

def truncar_16bits(valor):
    """
    Simula um registrador de 16 bits: só existem 65536 valores possíveis,
    de -32768 até 32767.
    """
    return ((valor + 32768) % 65536) - 32768

def obter_dado(endereco_str):
    """
    Define se o dado vem da memória (Endereçamento Direto)
    ou da própria instrução (Endereçamento Imediato).
    Retorna o valor inteiro a ser utilizado na operação.
    """
    if str(endereco_str).startswith('#'):
        # Endereçamento Imediato: o operando é o próprio dado.
        # Remove o '#' e converte para inteiro (aceita hex ou dec automaticamente pelo ', 0')
        return int(endereco_str.replace('#', ''), 0)
    else:
        # Endereçamento Direto: busca na memória.
        registradores['MAR'] = endereco_para_inteiro(endereco_str)
        registradores['MBR'] = memoria_ram[registradores['MAR']]
        return registradores['MBR']

# INSTRUÇÕES DE MEMÓRIA
def executar_load(partes):
    """
    LOAD M(x): AC <- MEM[x] (Endereçamento Direto)
    LOAD #x: AC <- x (Endereçamento Imediato)
    LOAD A, M(x): A <- MEM[x] (Endereçamento Direto em Registrador Específico)
    LOAD A, #x: A <- x (Endereçamento Imediato em Registrador Específico)
    LOAD A: AC <- A (Load de um Registrador Específico no AC)
    """
    token = partes[0].replace(',', '').upper()

    if len(partes) == 1 and reg_valido(token):
        # "LOAD A": AC <- A
        registradores['AC'] = registradores[token]
        atualizar_flags(registradores['AC'])
        return

    reg, endereco = parse_reg_e_endereco(partes)

    valor = obter_dado(endereco)

    registradores[reg] = valor
    atualizar_flags(registradores[reg])

def executar_loadI(endereco):
    """
    AC <- MEM[MEM[X]]  (indireto)
    """
    registradores['MAR'] = endereco_para_inteiro(endereco)
    registradores['MBR'] = memoria_ram[registradores['MAR']]
    registradores['MAR'] = registradores['MBR']
    registradores['MBR'] = memoria_ram[registradores['MAR']]
    registradores['AC'] = registradores['MBR']
    atualizar_flags(registradores['AC'])

def executar_store(partes):
    """
    STOR M(x): MEM[x] <- AC
    STOR A, M(x): MEM[x] <- A
    """
    reg, endereco = parse_reg_e_endereco(partes)
    registradores['MAR'] = endereco_para_inteiro(endereco)
    registradores['MBR'] = registradores[reg]
    memoria_ram[registradores['MAR']] = registradores['MBR']

def executar_storeI(endereco):
    # MEM[MEM[X]] <- AC  (indireto)
    registradores['MAR'] = endereco_para_inteiro(endereco)
    registradores['MBR'] = memoria_ram[registradores['MAR']]
    registradores['MAR'] = registradores['MBR']
    memoria_ram[registradores['MAR']] = registradores['AC']
    atualizar_flags(registradores['AC'])

# INSTRUÇÕES ARITMÉTICAS
def executar_add(partes):
    """
    ADD M(x): AC <- AC + MEM[x] (Endereçamento Direto)
    ADD #x: AC <- AC + x (Endereçamento Imediato)
    ADD A, M(x): A <- A + MEM[x] (Endereçamento Direto em Registrador Específico)
    ADD A, #x: A <- A + x (Endereçamento Imediato em Registrador Específico)
    """

    reg, endereco = parse_reg_e_endereco(partes)
    valor = obter_dado(endereco)

    resultado_bruto = registradores[reg] + valor
    registradores['C'] = 1 if (resultado_bruto > 32767 or resultado_bruto < -32768) else 0
    registradores[reg] = truncar_16bits(resultado_bruto)
    atualizar_flags(registradores[reg])

def executar_sub(partes):
    """
    SUB M(x): AC <- AC - MEM[x] (Endereçamento Direto)
    SUB #x: AC <- AC - x (Endereçamento Imediato)
    SUB A, M(x): A <- A - MEM[x] (Endereçamento Direto em Registrador Específico)
    SUB A, #x: A <- A - x (Endereçamento Imediato em Registrador Específico)
    """

    reg, endereco = parse_reg_e_endereco(partes)
    valor = obter_dado(endereco)

    resultado_bruto = registradores[reg] - valor
    registradores['C'] = 1 if (resultado_bruto > 32767 or resultado_bruto < -32768) else 0
    registradores[reg] = truncar_16bits(resultado_bruto)
    atualizar_flags(registradores[reg])

def executar_mult(partes):
    """
    MULT M(x): M:AC <- AC * MEM[x] (Endereçamento Direto)
    MULT #x: M:AC <- AC * x (Endereçamento Imediato)
    MULT A, M(x): M:A <- A * MEM[x] (Endereçamento Direto em Registrador Específico)
    MULT A, #x: M:A <- A * x (Endereçamento Imediato em Registrador Específico)
    """

    reg, endereco = parse_reg_e_endereco(partes)
    valor = obter_dado(endereco)

    resultado = registradores[reg] * valor
    registradores['M'] = (resultado >> 16) & 0xFFFF
    registradores[reg] = truncar_16bits(resultado % 65536)
    atualizar_flags(registradores[reg])

def executar_div(partes):
    """
    DIV M(x): AC <- AC / MEM[x], R <- resto  (Endereçamento Direto)
    DIV #x: AC <- AC / x, R <- resto (Endereçamento Imediato)
    DIV A, M(x): A <- A / MEM[x], R <- resto (Endereçamento Direto em Registrador Específico)
    DIV A, #x: A <- A / x, R <- resto (Endereçamento Imediato em Registrador Específico)
    """
    reg, endereco = parse_reg_e_endereco(partes)
    valor = obter_dado(endereco)

    if valor == 0:
        print("Erro: divisão por zero.")
        sys.exit(1)
        return

    registradores['R'] = registradores[reg] % valor
    registradores[reg] = registradores[reg] // valor
    atualizar_flags(registradores[reg])

# INSTRUÇÕES DE DESVIO
def executar_jump(endereco):
    # O endereço do salto passa pelo MAR antes de atualizar o PC
    registradores['MAR'] = endereco_para_inteiro(endereco)
    registradores['PC'] = registradores['MAR']

def executar_jump_positivo(endereco):
    # se AC >= 0: PC <- end
    if registradores["AC"] >= 0:
        registradores["PC"] = endereco_para_inteiro(endereco)

# MOVE
def executar_move(destino, origem='AC'):
    destino = destino.strip().upper()
    origem  = origem.strip().upper()

    if not reg_valido(destino):
        print(f"Erro MOV: registrador destino '{destino}' desconhecido.")
        return
    if not reg_valido(origem):
        print(f"Erro MOV: registrador origem '{origem}' desconhecido.")
        return

    registradores[destino] = registradores[origem]
    if destino == 'AC':
        atualizar_flags(registradores['AC'])

# DISPATCHER PRINCIPAL
def executar_instrucao(instrucao: str):
    partes = instrucao.strip().split()
    operacao = partes[0].upper()
    resto = partes[1:] # tudo após o mnemônico

    if operacao == 'LOAD':
        executar_load(resto)
    elif operacao == 'LOADI':
        executar_loadI(partes[-1])
    elif operacao in ('STORE', 'STOR'):
        executar_store(resto)
    elif operacao in ('STORI', 'STOREI'):
        executar_storeI(partes[-1])
    elif operacao == 'ADD':
        executar_add(resto)
    elif operacao == 'SUB':
        executar_sub(resto)
    elif operacao in ('MULT', 'MUL'):
        executar_mult(resto)
    elif operacao == 'DIV':
        executar_div(resto)
    elif operacao == 'JUMP':
        executar_jump(partes[-1])
    elif operacao == 'JUMP+':
        executar_jump_positivo(partes[-1])
    elif operacao == 'MOV':
        # "MOV destino, origem"  ou  "MOV destino" (origem implícita = AC)
        destino = partes[1].replace(',', '')
        origem  = partes[2].replace(',', '') if len(partes) >= 3 else 'AC'
        executar_move(destino, origem)
    else:
        print(f"Instrução desconhecida: {operacao}")
