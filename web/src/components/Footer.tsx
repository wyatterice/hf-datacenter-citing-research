// Dashboard footer, copied verbatim from the CIR dashboard (Footer.tsx).

export function Footer() {
  return (
    <footer className="dashboard-footer">
      <div className="footer-content">
        <span>Questions or feedback?</span>
        <a
          href="mailto:wtrolinger@heartlandforward.org,crews@heartlandforward.org?subject=Datacenter%20Impact%20Tool%20Inquiry"
          className="footer-email-link"
        >
          Contact Us
        </a>
      </div>
      <div className="footer-legal">
        <span>&copy; 2026 Heartland Forward. All rights reserved.</span>
        <span className="footer-separator">|</span>
        <span>110 NW 2nd Street, Bentonville, AR 72712</span>
        <span className="footer-separator">|</span>
        <a href="https://heartlandforward.org/privacy-policy/" target="_blank" rel="noopener noreferrer">
          Privacy Policy
        </a>
        <span className="footer-separator">|</span>
        <a href="https://heartlandforward.org/terms-conditions/" target="_blank" rel="noopener noreferrer">
          Terms &amp; Conditions
        </a>
      </div>
    </footer>
  )
}
