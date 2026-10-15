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

## Observação

Os dados continuam em memória como no protótipo web. A integração com a API `https://api.ciao.ao/api/v1` pode ser ligada posteriormente sem alterar a estrutura principal das telas.
