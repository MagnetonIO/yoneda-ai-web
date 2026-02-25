# yoneda-ai-web

Source repository for [yonedaai.com](https://yonedaai.com), the homepage of the YonedaAI Research Collective. Deployed via **Vercel** as a static site.

## Overview

This site serves as the central hub for the YonedaAI research program --- a systematic application of category theory (Yoneda lemma, presheaf semantics, Kan extensions, cohomological obstructions) to open problems in quantum mechanics, gravity, and observer theory.

The site links to two series of papers:

### Series 1 --- Foundational Problems (6 papers)

Hosted in [MagnetonIO/yoneda-ai](https://github.com/MagnetonIO/yoneda-ai). Six papers applying the Yoneda perspective to long-standing open problems: the black hole information paradox, hidden variable debates, the measurement problem, Wigner's friend scenarios, horizon problems, and limits of quantum gravity observation. Each paper includes a companion Haskell codebase and independent peer review.

### Series 2 --- Quantum Perspectivism (10 papers)

Ten papers developing Quantum Perspectivism as a complete interpretive and mathematical framework for quantum mechanics, built from the Yoneda Constraint. Each paper lives in its own repository under [MagnetonIO](https://github.com/MagnetonIO) and includes Haskell code and peer review.

## Deployment

Static site deployed via Vercel. No build step --- the `public/` directory is served directly.

```
public/
  index.html    # Main site
  images/       # Assets
  papers/       # Local PDF copies (if any)
```

## Author

**Matthew Long**
YonedaAI Research Collective
Chicago, IL
matthew@yonedaai.com
