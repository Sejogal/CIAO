# CIAO — React Native

Aplicação mobile nativa para o projeto **CIAO — Conecta IoT Angola**, convertida a partir do frontend React Web.

## Stack
- Expo SDK 57
- React Native 0.86
- Expo Router
- TypeScript
- React Native SVG
- Expo Vector Icons

## Executar

```bash
npm install
npx expo start
```

Atalhos:

```bash
npm run android
npm run ios
npm run web
npm run typecheck
```

O workflow do GitHub Actions executa `npm ci` e `npm run typecheck` para
cada push e pull request. A suíte backend também roda no workflow com
PostgreSQL 17.

## Conversão realizada

- Navegação TanStack Router → Expo Router
- Componentes HTML/Tailwind → componentes nativos React Native
- Radix UI → controles nativos (`Switch`, `Pressable`, `TextInput`, etc.)
- Lucide → Ionicons via Expo Vector Icons
- Recharts → SVG nativo para sparklines
- Layout responsivo de mobile preservado
- Tema visual aproximado ao frontend original: azul `#2563EB`, navy `#14213D`, fundo `#F5F7FB`, cartões brancos e sombras suaves
- Navegação inferior persistente nas áreas principais
- Fluxos de login, registo, empresas, projetos, dispositivos, datastreams, dashboards, automações, notificações, perfil e definições

## Integração com a API

Ligado ao backend real do CIAO (`@tanstack/react-query` + um cliente `fetch` próprio em `src/api/`):

- **Já ligado à API**: autenticação (login/registo/sessão via `expo-secure-store`), perfil (editar nome, avatar, idioma e fuso horário), empresas, projetos, dispositivos, datastreams/valores, dashboards/widgets, regras de automação e notificações internas.
- O cliente API normaliza erros HTTP, validação e falhas de rede; erros de consultas aparecem como aviso global e erros de formulários junto ao formulário.
- **Ainda sem integração externa**: notificações push/e-mail. Comandos de atuador já são publicados pelo backend em MQTT; o firmware precisa subscrever o tópico de comando e aplicar o valor recebido.
- A recuperação de palavra-passe continua pendente; não há fluxo de reset com verificação do utilizador.

### Configurar o URL do backend

O URL por defeito é `http://localhost:8000/api/v1` (`src/api/client.ts`), pensado para testar no browser (`npm run web`) com o backend a correr localmente. Para testar num emulador Android ou num telemóvel físico, define o URL correto no ecrã **Definições** da app (acessível também a partir do ecrã inicial, antes de entrar, pelo ícone de engrenagem):

- Emulador Android: `http://10.0.2.2:8000/api/v1`
- Telemóvel físico (mesma rede Wi-Fi do PC): `http://<IP local do PC>:8000/api/v1`

O backend (`ciao/backend`) tem de estar a correr e acessível nessa rede — ver o README desse projeto para o arrancar com `run_dev.py`, que já escuta em todas as interfaces.
