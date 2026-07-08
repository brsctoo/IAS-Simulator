# Simulador do Ciclo de Instrução — Arquitetura IAS

Simulador em Python do ciclo de busca, decodificação e execução de um processador baseado no modelo **IAS**, desenvolvido para a disciplina de Arquitetura e Organização de Computadores (UEM).

O simulador reproduz o comportamento de uma memória de 256 posições e de um conjunto de registradores especiais e de uso geral, executando programas escritos em uma linguagem de máquina simbólica definida para este projeto.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)
![License](https://img.shields.io/badge/license-educational-lightgrey)

---

## Índice

- [Visão geral](#visão-geral)
- [Arquitetura simulada](#arquitetura-simulada)
- [Conjunto de instruções](#conjunto-de-instruções)
- [Formato do arquivo de entrada](#formato-do-arquivo-de-entrada)
- [Como executar](#como-executar)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Programas de exemplo](#programas-de-exemplo)
- [Exemplo de execução](#exemplo-de-execução)
- [Decisões de projeto](#decisões-de-projeto)
- [Possíveis melhorias futuras](#possíveis-melhorias-futuras)
- [Autores](#autores)

---

## Visão geral

Todas as instruções e dados de um programa ficam armazenados em uma **memória RAM simulada de 256 posições** (endereços `0x00` a `0xFF`). A cada passo, o simulador executa o ciclo clássico:

```
MAR ← PC        (endereço da próxima instrução)
MBR ← MEM[MAR]  (busca a instrução)
IR  ← MBR       (carrega no registrador de instrução)
PC  ← PC + 1
executa a instrução
```

e imprime o estado completo dos registradores após cada instrução, permitindo acompanhar exatamente o que acontece dentro do processador a cada passo (pressionando ENTER para avançar).

## Arquitetura simulada

| Registrador | Função |
|---|---|
| `A`, `B` | Registradores de uso geral |
| `PC` | *Program Counter* — endereço da próxima instrução |
| `IR` | *Instruction Register* — instrução em execução |
| `MAR` | *Memory Address Register* — endereço em uso na memória |
| `MBR` | *Memory Buffer Register* — dado lido/gravado na memória |
| `AC` | Acumulador — destino padrão das operações aritméticas |
| `M` | Parte alta (16 bits) do resultado de `MULT` |
| `R` | Resto da divisão inteira de `DIV` |
| `C` | *Carry* — indica estouro (overflow) de `ADD`/`SUB` |
| `N` | Indica se o último valor manipulado é negativo |
| `Z` | Indica se o último valor manipulado é zero |

Os resultados aritméticos são tratados como palavras de **16 bits com sinal** (`-32768` a `32767`, complemento de 2). Quando uma soma ou subtração ultrapassa essa faixa, o valor "gira" (como um odômetro) e o registrador `C` é ativado.

## Conjunto de instruções

Baseado no computador IAS, com extensões pontuais para viabilizar acesso indexado a vetores.

| Instrução | Efeito | Observações |
|---|---|---|
| `LOAD M(x)` / `LOAD #x` | `AC ← MEM[x]` ou `AC ← x` | Direto ou imediato; aceita registrador explícito (`LOAD A, M(x)`) e `LOAD A` (`AC ← A`) |
| `LOADI M(x)` | `AC ← MEM[MEM[x]]` | Endereçamento indireto |
| `STORE` / `STOR` | `MEM[x] ← AC` (ou registrador indicado) | Não possui forma imediata — o destino é sempre um endereço |
| `STORI M(x)` | `MEM[MEM[x]] ← AC` | Endereçamento indireto para escrita |
| `ADD` / `SUB` | `reg ← reg + valor` / `reg ← reg − valor` | Resultado truncado para 16 bits; `C = 1` em caso de estouro |
| `MULT` | `M:reg ← reg × valor` | Resultado de 32 bits dividido em `M` (parte alta) e `reg` (parte baixa) |
| `DIV` | `reg ← reg ÷ valor`, `R ← resto` | Encerra o programa em caso de divisão por zero |
| `JUMP M(x)` | `PC ← x` | Desvio incondicional |
| `JUMP+ M(x)` | Se `AC ≥ 0`: `PC ← x` | Desvio condicional — salta quando `AC` é maior **ou igual** a zero |
| `MOV destino, origem` | `destino ← origem` | Origem padrão, se omitida, é `AC` |
| `HALT` | Encerra a execução | Extensão adicionada para marcar o fim do programa explicitamente |

`LOAD`, `ADD`, `SUB`, `MULT` e `DIV` aceitam tanto **endereçamento direto** (`M(x)`, busca na memória) quanto **endereçamento imediato** (`#x`, valor embutido na própria instrução), e opcionalmente um registrador de destino explícito (`A,` — se omitido, o padrão é `AC`).

## Formato do arquivo de entrada

Os programas são escritos em arquivos `.txt` divididos em três seções obrigatórias, marcadas por diretivas explícitas:

```
.DADOS
5
1
0x10

.INICIO
0x60

.CODIGO
LOAD M(0x01)
ADD M(0x00)
STOR M(0x02)
HALT
```

- **`.DADOS`** — valores iniciais (decimais ou hexadecimais com prefixo `0x`), carregados sequencialmente a partir do endereço `0x00`.
- **`.INICIO`** — endereço hexadecimal onde a primeira instrução será armazenada.
- **`.CODIGO`** — lista de instruções, posicionadas sequencialmente a partir do endereço definido em `.INICIO`.

Linhas iniciadas por `#` são comentários e são ignoradas (comentários apenas em linha inteira; não há suporte a comentário inline).

A execução termina ao encontrar `HALT`, uma posição de memória vazia (valor `0`), ou caso o `PC` ultrapasse os limites da memória.

## Como executar

Requer apenas **Python 3.8+** — nenhuma dependência externa.

```bash
python3 main.py selection_sort.txt
python3 main.py fibonacci.txt
python3 main.py truncamento_teste.txt
```

O simulador imprime o estado inicial dos registradores e, a cada instrução, pede `ENTER` para avançar, mostrando o novo estado. Ao final, o conteúdo da memória é exibido para conferência do resultado.

## Estrutura do repositório

```
.
├── memoria.py             # Estado global: memória RAM e dicionário de registradores
├── instrucoes.py          # Implementação do conjunto de instruções (ISA)
├── main.py                # Parser de entrada + ciclo de instrução (busca/decodificação/execução)
├── selection_sort.txt     # Programa de exemplo: ordenação por seleção
├── fibonacci.txt           # Programa de exemplo: sequência de Fibonacci
└── truncamento_teste.txt  # Programa de exemplo: estouro/truncamento aritmético de 16 bits
```

## Programas de exemplo

### `selection_sort.txt`
Ordena o vetor `[10, 3, 7, 2, 8]` usando o algoritmo *Selection Sort*, adaptado para caber na memória de 256 posições com ponteiros auxiliares (sem registrador de índice dedicado). Resultado esperado em `0x10`–`0x14`: `[2, 3, 7, 8, 10]`.

### `fibonacci.txt`
Calcula iterativamente os 10 primeiros termos da sequência de Fibonacci, usando `ADD` em laço controlado por `JUMP+`. Resultado esperado em `0x20`–`0x29`: `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`.

### `truncamento_teste.txt`
Valida o comportamento de estouro aritmético em 16 bits: soma que ultrapassa `32767`, subtração que ultrapassa `-32768`, uso normal sem estouro, e multiplicação que gera resultado de 32 bits dividido entre `M` e o registrador de destino.

## Exemplo de execução

```
Estado Inicial:
PC: 0x60 | MAR: 0x00
IR:  | MBR: 0x00
A: 0 | B: 0
AC: 0 | M: 0 | R: 0
C: 0 | N: 0 | Z: 0

Instrução a ser executada: LOAD M(0x01)
PC: 0x61 | MAR: 0x01
IR: LOAD M(0x01) | MBR: 0x01
AC: 1 | M: 0 | R: 0
C: 0 | N: 0 | Z: 0

...

--- Resultado na Memória ---
MEM[0x10] = 2
MEM[0x11] = 3
MEM[0x12] = 7
MEM[0x13] = 8
MEM[0x14] = 10
```

## Decisões de projeto

- **Instruções armazenadas como texto** (não como opcode binário), priorizando legibilidade e facilidade de depuração em um contexto didático.
- **Formato de entrada com seções explícitas** (`.DADOS` / `.INICIO` / `.CODIGO`), mais robusto do que depender de linhas em branco para separar blocos.
- **`STORE` não altera as flags `Z`/`N`**, já que a instrução grava um valor existente na memória sem modificar nenhum registrador.
- **`JUMP+` salta quando `AC ≥ 0`** (não apenas quando estritamente positivo), conforme convenção definida para este projeto.
- **Endereçamento indireto (`LOADI`/`STORI`)** foi adicionado como extensão ao conjunto básico do IAS, necessário para o `Selection Sort` acessar elementos de um vetor por endereço calculado dinamicamente.
- **Divisão por zero encerra a execução** imediatamente, evitando estados inconsistentes no simulador.

## Possíveis melhorias futuras

- Assembler simples com rótulos simbólicos, eliminando o cálculo manual de endereços de desvio.
- Representação das instruções em formato de opcode binário/numérico.
- Suporte a chamadas de procedimento, com salvamento e restauração de contexto.
- Modo de depuração com breakpoints e execução passo a passo configurável.
- Suíte de testes automatizados cobrindo cada instrução e seus casos de borda.

## Autores

- Felipe Almeida Gomes
- Diego Pimenta Suárez
- Bruno Rafael Comin Scheffel
- José Luís Peres de Sousa

Projeto acadêmico desenvolvido para a disciplina de Arquitetura e Organização de Computadores — Universidade Estadual de Maringá (UEM).
