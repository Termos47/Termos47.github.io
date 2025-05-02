// Получаем элементы DOM
const button = document.getElementById('changeButton');
const title = document.getElementById('title');
const body = document.body;

// Массив цветов для фона
const colors = ['#666666', '#000000',];

// Функция для изменения цвета
function changeBackgroundColor() {
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    body.style.backgroundColor = randomColor;
}

// Добавляем обработчик события на кнопку
button.addEventListener('click', changeBackgroundColor);

