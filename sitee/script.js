// Получаем элементы DOM
const button = document.getElementById('changeButton');
const title = document.getElementById('title');
const body = document.body;

// Массив цветов для фона
const colors = ['#000000', '#ffffff',];

// Функция для изменения цвета
function changeBackgroundColor() {
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    body.style.backgroundColor = randomColor;
}

// Добавляем обработчик события на кнопку
button.addEventListener('click', changeBackgroundColor);

