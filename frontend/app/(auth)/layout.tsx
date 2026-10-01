// templates/account/login.html and signup.html: the centred logo card.
// These pages use signup.css, not style.css (which hides .addpost).
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <link rel="stylesheet" href="/static/css/signup.css" />
      <div className="addpost">
        <div className="post-create">
          <img src="/images/logo.png" alt="AdderHub" className="auth-logo" />
          <div>{children}</div>
        </div>
      </div>
    </>
  );
}
