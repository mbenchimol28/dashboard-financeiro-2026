# Guia de Implantação e Integração com Google Sites

Este guia explica como colocar seu dashboard online gratuitamente e inseri-lo no seu portfólio do Google Sites.

## 1. Hospedagem do Dashboard
O Google Sites serve apenas para páginas estáticas (HTML/CSS/Imagens). Como seu dashboard usa Python (Dash/Pandas), ele precisa rodar em um servidor. Vamos usar o **Render** (opção gratuita e fácil).

### Passo 1: Preparar o Repositório no GitHub
1. Crie uma conta no [GitHub](https://github.com/) se não tiver.
2. Crie um novo repositório (ex: `dashboard-financeiro-2026`).
3. Faça upload dos arquivos do projeto para lá (ou use git push).
   - **Importante**: Certifique-se de que o arquivo `requirements.txt` e `app.py` estão na raiz.

### Passo 2: Publicar no Render.com
1. Crie uma conta no [Render](https://render.com/).
2. No painel, clique em **"New +"** e selecione **"Web Service"**.
3. Conecte sua conta do GitHub e selecione o repositório do dashboard.
4. Configure:
   - **Name**: `dashboard-financeiro` (ou outro nome único)
   - **Region**: Escolha a mais próxima (ex: Ohio - US East)
   - **Branch**: `main` (ou a branch que você usou)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server` (Isso requer que instalemos o `gunicorn`, veja a nota abaixo)
   - **Plan**: Free

> **Nota**: Adicione `gunicorn` ao seu `requirements.txt` antes de subir para o GitHub. É o servidor web de produção.

5. Clique em **"Create Web Service"**.
6. Aguarde o deploy finalizar. Você receberá uma URL (ex: `https://dashboard-financeiro.onrender.com`).

## 2. Integrar ao Google Sites

Agora que seu dashboard tem um link público, vamos colocá-lo no seu site.

1. Abra seu editor do **Google Sites**.
2. Vá para a página onde deseja exibir o dashboard.
3. No menu lateral direito (Inserir), clique em **"Incorporar"** (Embed).
4. Cole a URL do seu dashboard (ex: `https://dashboard-financeiro.onrender.com`).
5. Escolha **"Página inteira"** ou redimensione a caixa conforme necessário.
6. Publique as alterações no seu Google Sites.

## Dicas Adicionais
- **Responsividade**: Dashboards complexos podem ficar apertados em telas de celular. O design atual já é responsivo, mas verifique como fica no embed.
- **Segurança**: Como os dados são estáticos (carregados do CSV/Excel), não há risco de alguém alterar seus dados reais. O dashboard é "somente leitura" para os visitantes.
- **Performance**: O plano gratuito do Render "dorme" após 15 minutos de inatividade. O primeiro acesso pode levar cerca de 50 segundos para carregar. Para evitar isso, você pode usar serviços de "uptime monitor" (como UptimeRobot) para pingar seu site a cada 10 minutos.

---
**Checklist Rápido:**
- [ ] Adicionar `gunicorn` ao `requirements.txt`
- [ ] Subir código para o GitHub
- [ ] Deploy no Render
- [ ] Pegar URL e colar no Google Sites
