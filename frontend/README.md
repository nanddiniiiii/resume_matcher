# Frontend

Next.js, React, TypeScript and Tailwind CSS. See the [project README](../README.md#frontend) for setup.

```sh
npm ci
npm run dev
```

Set `NEXT_PUBLIC_API_URL` before building if the API is hosted elsewhere. All requests share `lib/config.ts`.

Checks: `npm run lint`, `npm run typecheck`, `npm run build`, `npm audit`.
