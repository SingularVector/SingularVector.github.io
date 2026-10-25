/* Post-only reading controls. No framework or network requests. */
(function () {
  'use strict';
  var article = document.querySelector('.page--post');
  if (!article) return;
  // This post-specific control owns copy feedback; leave non-post theme behavior alone.
  window.enable_copy_code_button = false;
  var desktop = window.matchMedia('(min-width: 1024px)');
  var author = document.querySelector('.sidebar--post .article-author');
  var authorToggle = author && author.querySelector('.article-author__toggle');
  var toc = article.querySelector('.article-toc');

  function updateLayout() {
    if (authorToggle) {
      author.classList.add('is-enhanced');
      author.classList.remove('is-expanded');
      authorToggle.hidden = desktop.matches;
      authorToggle.setAttribute('aria-expanded', 'false');
    }
    if (toc) toc.open = desktop.matches;
  }
  if (authorToggle) authorToggle.addEventListener('click', function () {
    var expanded = author.classList.toggle('is-expanded');
    authorToggle.setAttribute('aria-expanded', String(expanded));
  });
  if (desktop.addEventListener) desktop.addEventListener('change', updateLayout);
  else desktop.addListener(updateLayout);
  updateLayout();
  if (toc) toc.addEventListener('click', function (event) {
    if (!desktop.matches && event.target.closest('a[href^="#"]')) toc.open = false;
  });

  function fallbackCopy(text) {
    var input = document.createElement('textarea');
    input.value = text;
    input.setAttribute('readonly', '');
    input.style.cssText = 'position:fixed;top:0;left:0;opacity:0;';
    document.body.appendChild(input);
    input.select();
    var copied = false;
    try { copied = document.execCommand('copy'); } finally { input.remove(); }
    if (!copied) throw new Error('Clipboard unavailable');
  }

  article.querySelectorAll('.page__content pre > code').forEach(function (code) {
    var pre = code.parentElement;
    if (pre.closest('.article-code') || code.closest('.language-mermaid, .mermaid')) return;
    // The theme's copy setting may be enabled later; keep a single control.
    pre.querySelectorAll('.clipboard-copy-button').forEach(function (button) { button.remove(); });
    var wrapper = document.createElement('div');
    wrapper.className = 'article-code';
    pre.parentElement.insertBefore(wrapper, pre);
    var toolbar = document.createElement('div');
    toolbar.className = 'article-code__toolbar';
    var label = document.createElement('span');
    var languageNode = code.closest('[class*="language-"]');
    var language = languageNode && languageNode.className.match(/language-([\w-]+)/);
    var labels = { powershell: 'PowerShell', bash: 'Bash', shell: 'Shell', json: 'JSON', yaml: 'YAML', python: 'Python', text: 'Output', plaintext: 'Output' };
    label.textContent = language ? (labels[language[1]] || language[1]) : 'Code';
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'article-code__copy';
    button.textContent = 'Copy code';
    var status = document.createElement('span');
    status.className = 'sr-only';
    status.setAttribute('role', 'status');
    toolbar.appendChild(label);
    toolbar.appendChild(button);
    toolbar.appendChild(status);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(pre);
    pre.setAttribute('tabindex', '0');
    pre.setAttribute('aria-label', 'Code example; scroll horizontally for long lines');
    var reset;
    button.addEventListener('click', async function () {
      var actualCode = code.querySelector('td.rouge-code, td.code') || code;
      var text = actualCode.textContent;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          try { await navigator.clipboard.writeText(text); } catch (error) { fallbackCopy(text); }
        } else { fallbackCopy(text); }
        button.textContent = 'Copied';
        status.textContent = 'Code copied to clipboard.';
      } catch (error) {
        button.textContent = 'Copy failed';
        status.textContent = 'Copy failed. Select the code and copy it manually.';
      }
      button.focus({ preventScroll: true });
      window.clearTimeout(reset);
      reset = window.setTimeout(function () { button.textContent = 'Copy code'; status.textContent = ''; }, 2500);
    });
  });
})();
