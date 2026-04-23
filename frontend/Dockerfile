# Stage 1: build
FROM node:24-bullseye AS build
WORKDIR /app

# NEXT_PUBLIC_* vars must be present at build time so Next.js can bake them into the client bundle.
# Pass via --build-arg or rely on the default (prod URL).
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_ALWAYS_LOGGED_IN=false
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_ALWAYS_LOGGED_IN=$NEXT_PUBLIC_ALWAYS_LOGGED_IN

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: production
FROM node:24-bullseye AS production
WORKDIR /app

# Runtime env vars (for server-side code)
ENV NODE_ENV=production

# API_URL and ALWAYS_LOGGED_IN are read at runtime by the server — never baked into the build.
# Set via docker-compose env_file or environment section.

COPY --from=build /app/.next ./.next
COPY --from=build /app/package*.json ./
RUN npm install --only=production

EXPOSE 3000
CMD ["npm", "start"]
