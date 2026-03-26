# Product Guidelines

## Prose Style
- **Tone:** Technical and precise. All documentation and user-facing messages should be clear, direct, and technically accurate. Avoid unnecessary jargon where simple terms suffice, but prioritize precision over flowery language.
- **Audience:** Developers and system administrators. Assume technical competence but provide clear examples and rationales for complex operations.

## API & CLI Design
- **Priority:** Developer Experience (DX). The API should be intuitive and easy to use. Endpoints should follow logical patterns, and responses should be consistent.
- **Approach:** Self-documenting. Use clear naming conventions for endpoints, parameters, and models. The API structure should naturally guide the user towards the correct usage.
- **Error Handling:** Provide descriptive and actionable error messages. When an operation fails, explain *why* it failed and what the user can do to fix it.

## User Experience (UX)
- **Primary Interface:** REST API and CLI. Ensure that all functionality is accessible and well-documented through these interfaces.
- **Efficiency:** Minimize the number of steps required for common tasks (e.g., client creation, certificate generation).

## Code Quality & Engineering
- **Architecture:** Prioritize a modular and maintainable design. Logic should be consolidated into clean abstractions rather than being spread across multiple layers.
- **Maintainability:** Ensure that the codebase is easy to understand and extend. Follow established Python patterns and use type hinting extensively.
- **Validation:** Every change must be thoroughly tested and validated against the core requirements. Prioritize functional correctness and architectural integrity.
