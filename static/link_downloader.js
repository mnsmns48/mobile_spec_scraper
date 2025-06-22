function parsingObj(button) {
    if (!(button instanceof HTMLElement)) {
        console.error("Переданный объект не является DOM-элементом:", button);
        return;
    }

    const listItem = button.closest('li');
    if (!listItem) {
        console.error("Не удалось найти родительский <li> для кнопки");
        return;
    }

    const link = listItem.querySelector('a');
    if (!link) {
        console.error("Не удалось найти ссылку <a> внутри <li>");
        return;
    }

    const urlValue = link.getAttribute('href');
    if (!urlValue) {
        console.error("URL пустой или не найден");
        return;
    }

    const formData = new FormData();
    formData.append('url', urlValue);

    fetch('/add_info/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(text || 'Ошибка при отправке данных на сервер');
            });
        }
        return response.text();
    })
    .then(data => {
        console.log(urlValue, ': ok');
        listItem.remove();
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}
