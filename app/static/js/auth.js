
async function regFunction(event) {
  event.preventDefault();  // Предотвращаем стандартное действие формы

  // Получаем форму и собираем данные из неё
  const form = document.getElementById('data-form');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());


  const response = await fetch('/users/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  if (response.status == 409) {
    window.location.href = "/login";
    alert("User already exists")
    return;
  }
  try {
    // Проверяем успешность ответа
    if (!response.ok) {
      // Получаем данные об ошибке
      const errorData = await response.json();
      displayErrors(errorData);  // Отображаем ошибки
      return;  // Прерываем выполнение функции
    }

    const result = await response.json();
    if (result) {  // Проверяем наличие сообщения о успешной регистрации
      window.location.href = "/profile";  // Перенаправляем пользователя на страницу логина
    } else {
      alert(result.message || 'Unknown error');
    }
  } catch (error) {
    console.error('Ошибка:', error);
    alert('Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.');
  }

}
async function GetRegForm() {
  return window.location.href = "/register";
}

async function GetLogInForm() {
  return window.location.href = "/login";
}

async function loginFunction(event) {
  event.preventDefault();  // Предотвращаем стандартное действие формы

  // Получаем форму и собираем данные из неё
  const form = document.getElementById('data-form');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    // Проверяем успешность ответа
    if (response.status == 409) {
      window.location.href = "/profile";
      alert("You've already logged in");
      return;
    }

    if (response.status == 422 || response.status == 404) {
      alert("Invalid credentials");
      console.error("Invalid credentials");
      return;
    }

    if (response.status != 200) {
        alert("Something went wrong(")
        return;
    }
    const result = await response.json();

    if (result) {  // Проверяем наличие сообщения о успешной регистрации
      window.location.href = '/profile';  // Перенаправляем пользователя на страницу логина
    } else {
      alert(result.message || 'Неизвестная ошибка');
    }
  } catch (error) {
    console.error('Ошибка:', error);
    alert('Произошла ошибка при входе. Пожалуйста, попробуйте снова.');
  }
}


function displayErrors(errorData) {
  let message = 'Произошла ошибка';

  if (errorData && errorData.detail) {
    if (Array.isArray(errorData.detail)) {
      // Обработка массива ошибок
      message = errorData.detail.map(error => {
        if (error.type === 'string_too_short') {
          return `Поле "${error.loc[1]}" должно содержать минимум ${error.ctx.min_length} символов.`;
        }
        return error.msg || 'Произошла ошибка';
      }).join('\n');
    } else {
      // Обработка одиночной ошибки
      message = errorData.detail || 'Произошла ошибка';
    }
  }

  // Отображение сообщения об ошибке
  alert(message);
}

async function getMain() {
  const response = await fetch("/users/action", {
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    }
  })
  if (response.status == 200) {
    window.location.href = "/";
  } else {
    window.location.href = "/";
    alert("Sign in to continue")
  }
}

