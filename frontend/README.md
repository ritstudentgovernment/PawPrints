# PawPrints 2.0

PawPrints is a petition platform for the RIT Student Government built with [Next.js](https://nextjs.org/), designed to allow users to create, browse, and sign petitions. The platform integrates with RIT SG committees and provides a seamless user experience for managing petitions.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Features](#features)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Scripts](#scripts)
- [API Endpoints](#api-endpoints)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

---

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

---

## Features

- **User Authentication**: Login and logout functionality using SAML (RIT Shibboleth) authentication.
- **Petition Management**:
  - Create petitions with titles, descriptions, and tags.
  - View petition details, including updates and responses.
  - Sign petitions and track the number of signatures.
- **Committee Integration**: Filter petitions by committees and view committee-specific details.
- **Status Management**: Filter petitions by status (e.g., Active, Charged, Responded, Expired).
- **Responsive Design**: Fully responsive UI for desktop and mobile devices.

---

## Project Structure

```
pawprints-frontend/
├── src/
│   ├── app/
│   │   ├── api/                # API route handlers
│   │   ├── components/         # Reusable components (e.g., NavBar, Footer, Petition)
│   │   ├── create/             # Create petition page
│   │   ├── browse/             # Browse petitions page
│   │   ├── committees/         # Committees page
│   │   ├── hooks/              # Custom React hooks (e.g., useAuth)
│   │   ├── profile/            # User profile page
│   │   ├── globals.css         # Global CSS styles
│   │   ├── layout.tsx          # Root layout for the app
│   │   └── page.tsx            # Home page
│   ├── components/             # Shadcn UI components (e.g., buttons, cards, forms)
│   ├── assets/                 # Static assets (e.g., images, logos)
│   └── styles/                 # Additional CSS files
├── public/                     # Public assets (e.g., favicon, robots.txt)
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── package.json                # Project dependencies and scripts
├── Dockerfile                  # Docker file for deployment
└── README.md                   # Project documentation
```
---

## Scripts

The following scripts are available in the `package.json` file:

| Script         | Description                                      |
|----------------|--------------------------------------------------|
| `dev`          | Starts the development server.                  |
| `build`        | Builds the application for production.          |
| `start`        | Starts the production server.                   |
| `lint`         | Runs ESLint to check for code quality issues.    |

---

## API Endpoints

### Backend API

The application interacts with the backend API (configured via `NEXT_PUBLIC_API_URL`, default `http://localhost:8000`). Key endpoints include:

- **GET /api/v1/general/committee**: Fetches a list of committees.
- **POST /api/v1/general/old/search**: Searches for petitions based on query parameters.
- **POST /api/v1/petitions/:id/sign**: Signs a petition.

### Frontend API Routes

Custom API routes are defined in `src/app/api/specialRoute.ts`:

- `GET(query: string, page: number, items_per_page: number)`: Fetches petitions based on a query.
- `GETCommittee(query: string, page: number, items_per_page: number)`: Fetches petitions for a specific committee.
- `GETstatus(status: string, page: number, items_per_page: number)`: Fetches petitions by status.

---

## Technologies Used

### Frontend

- **Framework**: [Next.js](https://nextjs.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: React Hooks
- **UI Components**: Shadcn, Radix UI, Custom Components

### Backend

- **Authentication**: SAML with Passport.js
- **Server**: Express.js

### Other Tools

- **Form Validation**: [React Hook Form](https://react-hook-form.com/) with [Zod](https://zod.dev/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Utilities**: Class Variance Authority, clsx

## Using ShadCN Components

The PawPrints project leverages [ShadCN](https://ui.shadcn.com/docs/installation) components to build a modern, accessible, and customizable user interface. These components are built on top of [Radix UI](https://www.radix-ui.com/) primitives and styled using [Tailwind CSS](https://tailwindcss.com/), ensuring a consistent and responsive design system.

### Key Features of ShadCN Components
- **Accessibility**: Built with Radix UI primitives, ShadCN components ensure compliance with accessibility standards, making the application usable for all users.
- **Customizability**: Styled with Tailwind CSS, the components can be easily customized to match the branding and design requirements of PawPrints.
- **Reusability**: ShadCN components are modular and reusable, allowing for consistent UI patterns across the application.
- **TypeScript Support**: Full TypeScript support ensures type safety and a better developer experience.

### Examples of ShadCN Components in PawPrints
1. **Button**:
   - Used for actions like signing petitions, submitting forms, and navigation.
   - Example: `SignPetitionButton` in the petition detail page.
2. **Card**:
   - Used to display petition summaries in the petition list.
   - Example: Petition cards in the `PetitionContainer` component.
3. **Accordion**:
   - Used in the Committees page to display detailed information about each committee.
4. **Tabs**:
   - Used for navigation between different sections of the user profile or petition details.
5. **Select**:
   - Used in the sidebar for filtering petitions by committee.

---

## Contributing

### How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

### Code Style

- Follow the ESLint rules defined in the project.
- Use Prettier for consistent formatting.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
