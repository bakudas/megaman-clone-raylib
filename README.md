# Mega Man TDD: Um Estudo de Jogo de Plataforma com Python e Raylib

> Uma jornada de desenvolvimento de um jogo de plataforma 2D no estilo clássico, construído com foco em Test-Driven Development (TDD) e boas práticas de engenharia de software.

## Sobre o Projeto

Este repositório é um projeto de estudo para construir um jogo de plataforma inspirado em clássicos como _Mega Man X_. O objetivo principal não é apenas criar um jogo completo, mas também explorar e aplicar rigorosamente a metodologia **Test-Driven Development (TDD)** em um contexto de desenvolvimento de jogos, uma área onde essa prática é menos comum.

O projeto é desenvolvido em Python, utilizando a biblioteca Raylib para renderização e o Pytest para a suíte de testes.

## ✨ Features Implementadas

- **Motor de Física 2D:** Lógica de gravidade e colisões com o mundo.
- **Controle Total do Jogador:** Movimento horizontal, pulo e a habilidade de atirar.
- **Sistema de Plataformas:** Inclui tanto plataformas sólidas (que bloqueiam o jogador) quanto plataformas "pass-through" (que podem ser atravessadas por baixo).
- **Câmera Inteligente:** Câmera 2D suave que segue o jogador, com "look-ahead" inspirado nos clássicos do SNES.
- **Renderização em Resolução Nativa:** O jogo opera em uma resolução interna de 256x224 (padrão SNES) e é escalonado para uma janela maior, mantendo o aspect ratio e a nitidez dos pixels.

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.13
- **Biblioteca Gráfica:** Raylib (através do wrapper `raylib-py`)
- **Framework de Testes:** Pytest

## ⚙️ Como Executar

Para rodar o projeto localmente, siga estes passos:

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/bakudas/megaman-clone-raylib.git](https://github.com/bakudas/megaman-clone-raylib.git)
    cd megaman-clone-raylib
    ```

2.  **Execute o jogo:**
    ```bash
    # Sincroniza o projeto e baixa as ferramentas necessárias
    uv sync

    # Rodar o jogo
    uv run main.py
    ```

## 🛠️ Filosofia de Desenvolvimento

Este projeto segue um fluxo de trabalho estruturado:

- **Test-Driven Development (TDD):** A lógica de gameplay (física, colisões, estado do jogador) é testada antes de ser implementada.
- **Commits Semânticos:** O histórico do Git é mantido limpo e legível através de mensagens de commit padronizadas.
- **Branches de Feature/Fix:** O desenvolvimento é isolado em branches, garantindo que a `main` esteja sempre estável.

## 🗺️ Próximos Passos (Roadmap)

- [ ] Refatorar a lógica da câmera para uma classe `SmartCamera`.
- [ ] Implementar inimigos básicos com IA simples (patrulha).
- [ ] Adicionar um sistema de "vida" e dano para o jogador e inimigos.
- [ ] Desenvolver um sistema de câmera com transição de "salas".

---
