function toggleEdit(id) {
    var textElement_componente = document.getElementById('componente-text-' + id);
    var textElement_quantidade = document.getElementById('quantidade-number-' + id);
    var textElement_designator = document.getElementById('designator-text-' + id);
    var inputElement_quantidade = document.getElementById('componente-input-' + id);
    var inputElement_componente = document.getElementById('quantidade-input-' + id);
    var inputElement_designator = document.getElementById('designator-input-' + id);
    var saveButton = document.getElementById('save-button-' + id);
    
    // Alterna entre mostrar o texto e o campo de entrada
    if (inputElement_componente.style.display === "none") {
        textElement_componente.style.display = "none";
        textElement_quantidade.style.display = "none";
        textElement_designator.style.display = "none";
        inputElement_quantidade.style.display = "inline";
        inputElement_componente.style.display = "inline";
        inputElement_designator.style.display = "inline";
        saveButton.style.display = "inline";  // Mostrar o botão de salvar
    } else {
        textElement_componente.style.display = "inline";
        textElement_quantidade.style.display = "inline";
        textElement_designator.style.display = "inline";
        inputElement_quantidade.style.display = "none";
        inputElement_componente.style.display = "none";
        inputElement_designator.style.display = "none";
        saveButton.style.display = "none";  // Esconder o botão de salvar
    }
}


function toggleEdit2(id) {
    var TextElement_status = document.getElementById('status-text-' + id);
    var TextElement_changelog = document.getElementById('changelog-text-' + id);
    var TextElement_eng_resp = document.getElementById('eng-text-' + id);
    var TextElement_gpd_resp = document.getElementById('gpd-text-' + id);
    var TextElement_data_att = document.getElementById('data-att-text-' + id);
    var TextElement_obs = document.getElementById('obs-text-' + id);
    var InputElement_status = document.getElementById('status-input-' + id);
    var InputElement_changelog = document.getElementById('changelog-input-' + id);
    var InputElement_eng_resp = document.getElementById('eng-input-' + id);
    var InputElement_gpd_resp = document.getElementById('gpd-input-' + id);
    var InputElement_data_att = document.getElementById('data-att-input-' + id);
    var InputElement_obs = document.getElementById('obs-input-' + id);
    
    var saveButton = document.getElementById('save-button-' + id);
    
    
    // Alterna entre mostrar o texto e o campo de entrada para o status
    if (InputElement_status.style.display === "none") {

        TextElement_status.style.display = "none";
        TextElement_changelog.style.display = "none";
        TextElement_eng_resp.style.display = "none";
        TextElement_gpd_resp.style.display = "none";
        TextElement_data_att.style.display = "none";
        TextElement_obs.style.display = "none";

        InputElement_status.style.display = "inline";
        InputElement_changelog.style.display = "inline";
        InputElement_eng_resp.style.display = "inline";
        InputElement_gpd_resp.style.display = "inline";
        InputElement_data_att.style.display = "inline";
        InputElement_obs.style.display = "inline";

        saveButton.style.display = "inline";

    } else {
        TextElement_status.style.display = "inline";
        TextElement_changelog.style.display = "inline";
        TextElement_eng_resp.style.display = "inline";
        TextElement_gpd_resp.style.display = "inline";
        TextElement_data_att.style.display = "inline";
        TextElement_obs.style.display = "inline";

        InputElement_status.style.display = "none";
        InputElement_changelog.style.display = "none";
        InputElement_eng_resp.style.display = "none";
        InputElement_gpd_resp.style.display = "none";
        InputElement_data_att.style.display = "none";
        InputElement_obs.style.display = "none";

        saveButton.style.display = "none"; 
    }
}

