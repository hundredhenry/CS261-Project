function togglePasswordVisibility() {
    var password = document.getElementsByName('password')[0];
    var confirm_password = document.getElementsByName('confirm_password')[0];
    if (password.type === 'password') {
      password.type = 'text';
      confirm_password.type = 'text';
    } else {
      password.type = 'password';
      confirm_password.type = 'password';
    }
  }