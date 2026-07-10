import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// CIR brand design system, imported in cascade order.
import './styles/tokens.css'
import './styles/base.css'
import './styles/shared.css'
import './styles/footer.css'
import './styles/floating-nav.css'
// Tool-specific element styles.
import './styles/tool.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
