document.addEventListener('DOMContentLoaded', () => {
  const loginButton = document.querySelector('.login-pill');
  if (loginButton) {
    loginButton.addEventListener('click', () => {
      window.location.href = '/login';
    });
  }
});
