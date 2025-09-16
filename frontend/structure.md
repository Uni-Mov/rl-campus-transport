# Project Documentation

## Project Structure

The project is organized to encourage separation of concerns and modular development:

```
src/
├── api/          # Responsible for making requests to the backend (fetch, axios, etc.)
├── test/         # For test hooks or functions
├── hooks/        # Custom React hooks for encapsulating business logic
├── models/       # TypeScript interfaces and types shared across the app
├── components/   # React components, separated by levels of abstraction
│   ├── atoms/     # Small reusable UI elements (buttons, inputs, etc.)
│   ├── molecules/ # Mid-level components composed of smaller UI pieces
│   ├── organisms/ # Larger components composed of molecules/atoms
│   ├── templates/ # Page-level layouts that define structure
│   └── pages/     # Concrete instances of templates with real content
```

---

## About Design Pattern

This project follows the [Atomic Design](https://atomicdesign.bradfrost.com/chapter-2/) methodology proposed by Brad Frost.  
The pattern is based on the idea of atoms, molecules, organisms, templates, and pages, which represent the fundamental building blocks of any interface:

- **Atom**: the most basic element of the interface (e.g., a button, an input field).
- **Molecule**: a combination of atoms, such as a search form composed of an input (atom) and a button (atom).
- **Organism**: a more complex component grouping multiple molecules and atoms, like a website header with a logo, navigation menu, and search form.
- **Template**: defines the structure of a page (e.g., homepage layout with header, main content, and footer), without real content.
- **Page**: a concrete instance of a template filled with actual data, such as a blog homepage showing text, images, and links.

In this template, to simplify development and leverage **Tailwind CSS** and **reusable components**, we focus primarily on the **organism** and **template** levels, instead of defining every atom or molecule individually.

---

## Running the Project

### Templates
```bash
npm install   # only the first time
npm run dev   # start development server
```

### Tests
```bash
npm test
```

---

## Notes

- **Tailwind CSS** is used for styling, ensuring consistency and scalability across components.
- **TypeScript** provides type safety and facilitates maintainability.
- **Reusable components** are prioritized to reduce duplication and improve code clarity.
