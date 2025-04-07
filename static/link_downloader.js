function parsingObj(button) {
    if (button instanceof HTMLElement) {
        const listItem = button.closest('li');
        if (listItem) {
            const link = listItem.querySelector('a');
            if (link) {
                const urlData = {
                    url: link.getAttribute('href')
                };
                fetch('/add_info/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(urlData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка при отправке данных на сервер');
                    }
                    return response.text();
                })
                .then(data => {
                    console.log(urlData.url, ': ok');
                    listItem.remove();
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                });
            } else {
                console.error("Не удалось найти ссылку <a> внутри <li>");
            }
        } else {
            console.error("Не удалось найти родительский <li> для кнопки");
        }
    } else {
        console.error("Переданный объект не является DOM-элементом:", button);
    }
}
