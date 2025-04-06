console.log("Скрипт работает для страницы link_for_pars.html");
document.querySelectorAll('#links-list a').forEach(link => {
    link.addEventListener('mouseover', () => {
        link.style.color = 'red';
    });
    link.addEventListener('mouseout', () => {
        link.style.color = '';
    });
});

function removeLink(button) {
    // Проверяем, является ли button DOM-элементом
    if (button instanceof HTMLElement) {
        const listItem = button.closest('li'); // Находим ближайший родительский элемент <li>
        if (listItem) {
            listItem.remove(); // Удаляем элемент списка
            console.log("Элемент списка удален:", listItem);
        } else {
            console.error("Не удалось найти родительский <li> для кнопки");
        }
    } else {
        console.error("Переданный объект не является DOM-элементом:", button);
    }
}
