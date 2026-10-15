# Notas de migração

## Web → React Native

| Web | Native |
|---|---|
| TanStack Router | Expo Router |
| `<div>`, `<section>` | `<View>` |
| `<p>`, `<h1>` | `<Text>` |
| `<input>` | `<TextInput>` |
| `<button>` / `<a>` | `<Pressable>` |
| Tailwind CSS | `StyleSheet` |
| Radix UI | Componentes nativos |
| lucide-react | `@expo/vector-icons` |
| Recharts/SVG web | `react-native-svg` (sparkline simples) |
| useSyncExternalStore | Mantido para o estado demo |

O estado e os dados demo do projeto web foram preservados em `src/store.ts`.

## Telas convertidas

- Welcome
- Login / Registo / Recuperação
- Início
- Dashboards
- Empresas + detalhe + nova empresa
- Projetos + detalhe + novo projeto
- Dispositivos + detalhe + novo dispositivo
- Datastream + novo datastream
- Automações + nova automação
- Notificações
- Perfil
- Definições
- Provisionamento

## Próximo passo recomendado

O projeto web original ainda contém lógica específica de browser e componentes Radix/Tailwind. Esta versão substitui essas dependências por APIs nativas e está preparada para receber a integração real com a API em `prefs.apiUrl`.
