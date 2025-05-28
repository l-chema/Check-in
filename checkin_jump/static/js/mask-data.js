document.addEventListener('DOMContentLoaded', function () {
    const inputsData = document.querySelectorAll('.mascara-data');

    inputsData.forEach(function (input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é número

            if (value.length > 2) {
                value = value.slice(0, 2) + '/' + value.slice(2);
            }
            if (value.length > 5) {
                value = value.slice(0, 5) + '/' + value.slice(5, 9);
            }
            e.target.value = value.slice(0, 10); // Limita a 10 caracteres (dd/mm/aaaa)
        });
    });
});