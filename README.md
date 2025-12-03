# 🖱️ Clicker Script Editor

Editor visual de scripts de automação para criação e execução de sequências de ações automatizadas (cliques, digitação, atalhos de teclado, etc.) com suporte a agendamento.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Criando um Executável](#-criando-um-executável)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## 🎯 Sobre o Projeto

O **Clicker Script Editor** é uma aplicação desktop desenvolvida em Python que permite criar, editar e executar scripts de automação de forma visual e intuitiva. Com ele, você pode:

- Criar sequências complexas de ações automatizadas
- Agendar execuções em horários específicos
- Salvar e reutilizar scripts
- Executar ações como cliques, digitação, atalhos de teclado e muito mais

## ✨ Funcionalidades

### 🎨 Interface Gráfica Intuitiva
- Interface moderna e fácil de usar
- Suporte a temas (DarkGray15 e SystemDefault1)
- Visualização em tempo real dos passos do script

### 🖱️ Tipos de Ações Suportadas
- **Clique Simples** - Clique em coordenadas específicas
- **Clique Duplo** - Duplo clique em coordenadas específicas
- **Digitar Texto** - Digitação automática de texto
- **Esperar** - Pausa por tempo determinado
- **Pressionar Tecla** - Pressionar uma tecla específica
- **Atalho de Teclado** - Executar combinações de teclas (Ctrl+C, Alt+Tab, etc.)
- **Abrir Aplicativo** - Abrir aplicativos (Chrome com suporte a modo anônimo e tamanho personalizado)
- **Redimensionar Janela** - Redimensionar janelas abertas

### ⏰ Agendamento
- Agendar execução de scripts em horários específicos
- Múltiplos horários por script
- Ativação/desativação fácil do agendamento

### 💾 Gerenciamento de Scripts
- Salvar e carregar scripts
- Editar scripts existentes
- Deletar scripts
- Organizar passos (mover para cima/baixo)

### 🖥️ Recursos Avançados
- Captura de posição do mouse com delay
- Suporte a múltiplos monitores (Chrome sempre abre na tela principal)
- Modo anônimo do Chrome
- Redimensionamento automático de janelas

## 📦 Requisitos

- **Python 3.10+**
- **Windows** (testado no Windows 10/11)
- Bibliotecas listadas em `requirements.txt`

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/bryangama/clicker-script-editor.git
cd clicker-script-editor
```

### 2. Crie um ambiente virtual (recomendado)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```powershell
pip install -r requirements.txt
```

**Dependências principais:**
- `FreeSimpleGUI` - Interface gráfica
- `pyautogui` - Automação de mouse/teclado
- `schedule` - Agendamento de tarefas
- `pywin32` - Funcionalidades avançadas do Windows (opcional, mas recomendado)

## 💻 Como Usar

### Executando o Aplicativo

```powershell
python listagem.py
```

### Criando um Script

1. **Digite o nome do script** no campo "Nome do Script"
2. **Adicione passos** clicando em "Adicionar Passo"
3. **Configure cada passo**:
   - Selecione o tipo de ação
   - Configure os parâmetros necessários
   - Defina o delay antes da execução
   - (Opcional) Dê um nome ao passo
4. **Organize os passos** usando "Mover para Cima" ou "Mover para Baixo"
5. **Salve o script** clicando em "Salvar Script"

### Executando um Script

1. **Carregue um script** da lista ou crie um novo
2. Clique em **"Executar Script"**
3. Acompanhe o progresso no log de execução
4. Use **"Parar Execução"** para interromper se necessário

### Agendando um Script

1. **Carregue ou crie um script**
2. **Adicione horários** no formato HH:MM (ex: 14:30)
3. Clique em **"Add Hora"** para cada horário desejado
4. **Ative o agendamento** marcando a checkbox "Ativar Agendamento"
5. O script será executado automaticamente nos horários configurados

### Exemplo de Script

Um script simples para abrir o Chrome e fazer uma busca:

1. **Abrir Aplicativo**: Chrome (800x600)
2. **Esperar**: 3 segundos
3. **Digitar Texto**: "Python automation"
4. **Pressionar Tecla**: Enter
5. **Esperar**: 2 segundos

## 🔨 Criando um Executável

Para criar um arquivo executável (.exe) do aplicativo:

### Método 1: Script Automatizado (Recomendado)

```powershell
python build_exe.py
```

### Método 2: Arquivo Batch

Duplo clique em `criar_exe.bat`

### Método 3: Comando Direto

```powershell
pyinstaller ClickerScriptEditor.spec
```

O executável será criado em `dist/ClickerScriptEditor.exe`

**Nota:** Consulte `BUILD_INSTRUCTIONS.md` para instruções detalhadas.

### ⚠️ Problema Comum: Erro "No module named 'FreeSimpleGUI'"

Se ao executar o .exe em outro computador você receber o erro `No module named 'FreeSimpleGUI'`, isso significa que o executável foi criado sem incluir corretamente todas as dependências.

**Solução:**
1. Use sempre o arquivo `.spec` atualizado ou o script `build_exe.py`
2. Limpe builds anteriores antes de reconstruir:
   ```powershell
   # PowerShell
   Remove-Item -Path build,dist -Recurse -Force -ErrorAction SilentlyContinue
   pyinstaller ClickerScriptEditor.spec --clean
   ```
   
   Ou se estiver usando CMD:
   ```cmd
   rmdir /s /q build dist
   pyinstaller ClickerScriptEditor.spec --clean
   ```
3. O arquivo `.spec` já está configurado para incluir todas as dependências necessárias do FreeSimpleGUI

**Importante:** Não use comandos PyInstaller simples sem as flags necessárias, pois podem não incluir todas as dependências.

### Distribuição

O executável é portátil e pode ser distribuído sozinho. Os scripts salvos são armazenados na mesma pasta do executável:
- `scripts/` - Pasta com os scripts salvos
- `scripts_list.json` - Lista de scripts

## 📁 Estrutura do Projeto

```
clicker-script-editor/
│
├── 📄 listagem.py              # Aplicativo principal
├── 📄 config.py                # Configurações e constantes
├── 📄 script_manager.py        # Gerenciamento de arquivos
├── 📄 script_executor.py       # Execução de scripts
├── 📄 gui_components.py        # Componentes de interface
├── 📄 scheduler.py             # Agendamento
├── 📄 utils.py                 # Funções utilitárias
│
├── 📄 requirements.txt         # Dependências do projeto
├── 📄 README.md                # Este arquivo
├── 📄 BUILD_INSTRUCTIONS.md    # Instruções de build
├── 📄 .gitignore               # Arquivos ignorados pelo Git
│
├── 🔧 build_exe.py             # Script para criar executável
├── 🔧 criar_exe.bat            # Batch para Windows
├── 🔧 ClickerScriptEditor.spec # Configuração PyInstaller
│
└── 📁 scripts/                 # Scripts salvos (criado automaticamente)
    └── *.json                  # Arquivos de script
```

## 🛠️ Tecnologias Utilizadas

- **[FreeSimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)** - Framework para interface gráfica
- **[PyAutoGUI](https://github.com/asweigart/pyautogui)** - Automação de mouse e teclado
- **[Schedule](https://github.com/dbader/schedule)** - Agendamento de tarefas
- **[PyInstaller](https://www.pyinstaller.org/)** - Criação de executáveis
- **[pywin32](https://github.com/mhammond/pywin32)** - Funcionalidades do Windows

## 📝 Exemplos de Uso

### Exemplo 1: Automação de Login

```
1. Abrir Aplicativo: Chrome
2. Esperar: 2s
3. Clique em: (500, 300) - Campo de usuário
4. Digitar: "meu_usuario"
5. Pressionar: Tab
6. Digitar: "minha_senha"
7. Pressionar: Enter
```

### Exemplo 2: Navegação Web

```
1. Abrir Aplicativo: Chrome (1920x1080)
2. Esperar: 3s
3. Atalho: Ctrl+L (abrir barra de endereço)
4. Digitar: "https://github.com"
5. Pressionar: Enter
6. Esperar: 5s
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## ⚠️ Avisos Importantes

- **Uso Responsável**: Este software é para fins legítimos de automação. Use com responsabilidade.
- **Antivírus**: Executáveis criados com PyInstaller podem ser marcados como suspeitos por alguns antivírus (falso positivo comum).
- **Permissões**: Algumas ações podem requerer permissões administrativas dependendo do sistema.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👤 Autor

**Bryan Catani Gama**
- GitHub: [@bryangama](https://github.com/bryangama)

## 🙏 Agradecimentos

- Comunidade Python
- Desenvolvedores das bibliotecas utilizadas
- Todos os contribuidores

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
