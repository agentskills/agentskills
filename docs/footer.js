// Mintlify's `footer` setting in docs.json only supports links and social icons,
// so the legal notice is added here. Mintlify swaps page content without a full
// reload and may re-render the footer, so watch for the footer appearing again.
function addLegalNotice() {
  const footer = document.querySelector("footer#footer");
  if (!footer || footer.querySelector(".legal-notice")) return;

  const copyright = document.createElement("p");
  copyright.textContent = "Copyright © Agent Skills a Series of LF Projects, LLC";

  const link = document.createElement("a");
  link.href = "https://lfprojects.org";
  link.textContent = "lfprojects.org";

  const policies = document.createElement("p");
  policies.append(
    "For web site terms of use, trademark policy and other project policies please see ",
    link,
    ".",
  );

  const notice = document.createElement("div");
  notice.className = "legal-notice";
  notice.append(copyright, policies);
  footer.append(notice);
}

new MutationObserver(addLegalNotice).observe(document.body, {
  childList: true,
  subtree: true,
});
addLegalNotice();
