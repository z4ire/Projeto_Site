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

function toggleEdit2(id) {
    var statusTextElement = document.getElementById('status-text-' + id);  // Elemento que exibe o texto do status
    var statusInputElement = document.getElementById('status-input-' + id);  // Elemento de entrada de texto para edição do status
    var saveButton = document.getElementById('save-button-' + id);  // Botão de salvar
    
    // Alterna entre mostrar o texto e o campo de entrada para o status
    if (statusInputElement.style.display === "none") {
        statusTextElement.style.display = "none";  // Esconde o texto do status
        statusInputElement.style.display = "inline";  // Exibe o campo de entrada para edição
        saveButton.style.display = "inline";  // Exibe o botão de salvar

    } else {
        statusTextElement.style.display = "inline";  // Exibe o texto do status novamente
        statusInputElement.style.display = "none";  // Esconde o campo de entrada
        saveButton.style.display = "none";  // Esconde o botão de salvar
    }
}

