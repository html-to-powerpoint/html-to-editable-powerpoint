document.querySelectorAll('pre').forEach((pre, index) => {
  const code = pre.querySelector('code');
  if (!code || !navigator.clipboard) return;
  const controls = document.createElement('div');
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-code';
  button.textContent = 'Copy code';
  button.setAttribute('aria-label', `Copy code example ${index + 1}`);
  const status = document.createElement('span');
  status.className = 'copy-status';
  status.setAttribute('role', 'status');
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.textContent);
      status.textContent = 'Copied';
    } catch {
      status.textContent = 'Copy unavailable. Select and copy the code below.';
    }
  });
  controls.append(button, status);
  pre.before(controls);
});
