function toggleEdit(id) {
    var textElement = document.getElementById('componente-text-' + id);
    var inputElement = document.getElementById('componente-input-' + id);
    var saveButton = document.getElementById('save-button-' + id);
    
    // Alterna entre mostrar o texto e o campo de entrada
    if (inputElement.style.display === "none") {
        textElement.style.display = "none";
        inputElement.style.display = "inline";
        saveButton.style.display = "inline";  // Mostrar o botão de salvar
    } else {
        textElement.style.display = "inline";
        inputElement.style.display = "none";
        saveButton.style.display = "none";  // Esconder o botão de salvar
    }
}